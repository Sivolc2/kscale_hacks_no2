import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { LoadingManager } from 'three';
import URDFLoader from 'urdf-loader/umd/URDFLoader.js';

// Backend configuration
const BACKEND_URL = 'http://192.168.154.196:5005';

class RobotVisualizer {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.controls = null;
        this.robot = null;
        this.urdfLoader = null;
        this.defaultRobot = new THREE.Group();
        this.parts = {};
        this.streamConnection = null;
        
        this.init();
        this.setupControls();
        this.createDefaultRobot();
        this.setDefaultPose();
        this.animate();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        document.getElementById('scene-container').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 50;
        this.camera.position.y = 30;
        this.camera.lookAt(0, 0, 0);

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 10);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);

        // Add coordinate grid
        const gridHelper = new THREE.GridHelper(100, 10);
        this.scene.add(gridHelper);

        // Setup URDF loader with proper loading manager
        const manager = new LoadingManager();
        this.urdfLoader = new URDFLoader(manager);
        this.urdfLoader.loadMeshCb = (path, manager, onComplete) => {
            const loader = new STLLoader(manager);
            loader.load(path, onComplete);
        };

        // Add default robot group to scene
        this.scene.add(this.defaultRobot);

        window.addEventListener('resize', () => this.onWindowResize(), false);
    }

    setupControls() {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
    }

    loadURDF(urdfPath) {
        // Remove existing robot if any
        if (this.robot) {
            this.scene.remove(this.robot);
        }

        // Hide default robot
        this.defaultRobot.visible = false;

        // Load URDF
        this.urdfLoader.load(
            urdfPath,
            (urdfRobot) => {
                this.robot = urdfRobot;
                this.scene.add(urdfRobot);
                console.log('URDF loaded successfully:', urdfRobot);
                
                // Center the robot
                const box = new THREE.Box3().setFromObject(urdfRobot);
                const center = box.getCenter(new THREE.Vector3());
                urdfRobot.position.sub(center);
                urdfRobot.position.y = 0; // Place on ground
                
                // Update status
                document.getElementById('status').textContent = 'URDF loaded successfully';
            },
            (progress) => {
                const percent = (progress.loaded / progress.total * 100).toFixed(2);
                document.getElementById('status').textContent = `Loading URDF: ${percent}%`;
            },
            (error) => {
                console.error('Error loading URDF:', error);
                document.getElementById('status').textContent = 'Error loading URDF';
                this.defaultRobot.visible = true; // Show default robot on error
            }
        );
    }

    createRobotPart(geometry, material, name) {
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        this.parts[name] = mesh;
        return mesh;
    }

    createDefaultRobot() {
        const robotMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x666666,
            specular: 0x111111,
            shininess: 30
        });

        // Torso
        const torso = this.createRobotPart(
            new THREE.BoxGeometry(8, 12, 4),
            robotMaterial,
            'torso'
        );
        this.defaultRobot.add(torso);

        // Head
        const head = this.createRobotPart(
            new THREE.SphereGeometry(2.5, 32, 32),
            robotMaterial,
            'head'
        );
        head.position.y = 8;
        torso.add(head);

        // Eyes
        const eyeMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        const leftEye = this.createRobotPart(
            new THREE.SphereGeometry(0.5, 16, 16),
            eyeMaterial,
            'leftEye'
        );
        leftEye.position.set(1, 0.5, 2);
        head.add(leftEye);

        const rightEye = this.createRobotPart(
            new THREE.SphereGeometry(0.5, 16, 16),
            eyeMaterial,
            'rightEye'
        );
        rightEye.position.set(-1, 0.5, 2);
        head.add(rightEye);

        // Arms
        const armGeometry = new THREE.BoxGeometry(2, 8, 2);
        const leftArm = this.createRobotPart(armGeometry, robotMaterial, 'leftArm');
        leftArm.position.set(5, 0, 0);
        torso.add(leftArm);

        const rightArm = this.createRobotPart(armGeometry, robotMaterial, 'rightArm');
        rightArm.position.set(-5, 0, 0);
        torso.add(rightArm);

        // Legs
        const legGeometry = new THREE.BoxGeometry(3, 10, 3);
        const leftLeg = this.createRobotPart(legGeometry, robotMaterial, 'leftLeg');
        leftLeg.position.set(2.5, -11, 0);
        torso.add(leftLeg);

        const rightLeg = this.createRobotPart(legGeometry, robotMaterial, 'rightLeg');
        rightLeg.position.set(-2.5, -11, 0);
        torso.add(rightLeg);
    }

    setDefaultPose() {
        // Reset all rotations
        Object.values(this.parts).forEach(part => {
            part.rotation.set(0, 0, 0);
        });

        // Set default standing pose
        this.defaultRobot.position.y = 11; // Lift robot to stand on grid
        
        // Slightly bend arms outward
        if (this.parts.leftArm) {
            this.parts.leftArm.rotation.z = -Math.PI * 0.1;
        }
        if (this.parts.rightArm) {
            this.parts.rightArm.rotation.z = Math.PI * 0.1;
        }
    }

    updateRobotPose(poseData) {
        if (!poseData) {
            this.setDefaultPose();
            return;
        }

        if (this.robot) {
            // Update URDF robot joints
            Object.entries(poseData).forEach(([jointName, rotation]) => {
                if (this.robot.joints[jointName]) {
                    this.robot.setJointValue(jointName, THREE.MathUtils.degToRad(rotation));
                }
            });
        } else {
            // Update default robot parts
            Object.entries(poseData).forEach(([partName, rotation]) => {
                const part = this.parts[partName];
                if (part) {
                    part.rotation.set(
                        THREE.MathUtils.degToRad(rotation.x || 0),
                        THREE.MathUtils.degToRad(rotation.y || 0),
                        THREE.MathUtils.degToRad(rotation.z || 0)
                    );
                }
            });
        }
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    startStreamingMotion() {
        if (this.streamConnection) {
            this.streamConnection.close();
        }

        this.streamConnection = new EventSource(`${BACKEND_URL}/stream_motion`);
        
        this.streamConnection.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.pose) {
                this.updateRobotPose(data.pose);
            }
        };

        this.streamConnection.onerror = (error) => {
            console.error('Stream connection error:', error);
            document.getElementById('status').textContent = 'Streaming error - check console and backend connection';
            // Close the connection on error
            this.stopStreamingMotion();
            streamButton.textContent = 'Start Streaming';
        };

        document.getElementById('status').textContent = 'Streaming motion data...';
    }

    stopStreamingMotion() {
        if (this.streamConnection) {
            this.streamConnection.close();
            this.streamConnection = null;
            document.getElementById('status').textContent = 'Streaming stopped';
            this.setDefaultPose();
        }
    }
}

// Initialize the visualizer
const visualizer = new RobotVisualizer();

// Setup URDF loading
document.getElementById('load-urdf-btn').addEventListener('click', () => {
    document.getElementById('urdf-input').click();
});

document.getElementById('urdf-input').addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const urdfContent = e.target.result;
            // Create a blob URL for the URDF content
            const blob = new Blob([urdfContent], { type: 'text/xml' });
            const urdfUrl = URL.createObjectURL(blob);
            visualizer.loadURDF(urdfUrl);
        };
        reader.readAsText(file);
    }
});

// Add streaming control buttons
const streamButton = document.createElement('button');
streamButton.textContent = 'Start Streaming';
streamButton.addEventListener('click', () => {
    if (streamButton.textContent === 'Start Streaming') {
        visualizer.startStreamingMotion();
        streamButton.textContent = 'Stop Streaming';
    } else {
        visualizer.stopStreamingMotion();
        streamButton.textContent = 'Start Streaming';
    }
});

// Insert the stream button before the validate button
const controls = document.getElementById('controls');
const validateBtn = document.getElementById('validate-btn');
controls.insertBefore(streamButton, validateBtn);

// Setup the validate button
document.getElementById('validate-btn').addEventListener('click', async () => {
    const statusElement = document.getElementById('status');
    statusElement.textContent = 'Validating...';
    
    try {
        const response = await fetch(`${BACKEND_URL}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Source-File': 'web-visualizer'
            },
            body: JSON.stringify({
                pose: {
                    leftArm: { x: 0, y: 0, z: -45 },  // Example pose data
                    rightArm: { x: 0, y: 0, z: 45 }
                }
            })
        });

        const data = await response.json();
        visualizer.updateRobotPose(data.pose);
        statusElement.textContent = 'Pose updated';
    } catch (error) {
        statusElement.textContent = 'Error: ' + error.message;
        console.error('Error:', error);
        visualizer.setDefaultPose();  // Reset to default pose on error
    }
}); 