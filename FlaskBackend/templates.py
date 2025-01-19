"""HTML templates for the Flask backend."""

LANDING_PAGE = """
<html>
<head>
    <title>Hand IK Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; }
        .endpoint { margin-bottom: 30px; background: #f5f5f5; padding: 20px; border-radius: 5px; }
        pre { background: #eee; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .status { display: inline-block; padding: 5px 10px; border-radius: 3px; }
        .enabled { background: #90EE90; }
        .disabled { background: #FFB6C1; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hand IK Server</h1>
        
        <div class="endpoint">
            <h2>Server Status</h2>
            <p>IK Processing: <span class="status {{ 'enabled' if config.get('ENABLE_IK', False) else 'disabled' }}">
                {{ 'Enabled' if config.get('ENABLE_IK', False) else 'Disabled' }}
            </span></p>
            <p>IK Plotting: <span class="status {{ 'enabled' if config.get('PLOT_IK', False) else 'disabled' }}">
                {{ 'Enabled' if config.get('PLOT_IK', False) else 'Disabled' }}
            </span></p>
        </div>

        <div class="endpoint">
            <h2>Hand Points Reference</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                </tr>
                <!-- Wrist -->
                <tr>
                    <td>0</td>
                    <td>handWrist</td>
                    <td>Main wrist joint</td>
                </tr>
                <!-- Thumb -->
                <tr>
                    <td>1</td>
                    <td>handThumbKnuckle</td>
                    <td>Base of thumb</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>handThumbIntermediateBase</td>
                    <td>First thumb joint</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>handThumbIntermediateTip</td>
                    <td>Second thumb joint</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>handThumbTip</td>
                    <td>Tip of thumb</td>
                </tr>
                <!-- Index Finger -->
                <tr>
                    <td>5</td>
                    <td>handIndexFingerMetacarpal</td>
                    <td>Base of index finger in palm</td>
                </tr>
                <tr>
                    <td>6</td>
                    <td>handIndexFingerKnuckle</td>
                    <td>Index finger knuckle</td>
                </tr>
                <tr>
                    <td>7</td>
                    <td>handIndexFingerIntermediateBase</td>
                    <td>First index finger joint</td>
                </tr>
                <tr>
                    <td>8</td>
                    <td>handIndexFingerIntermediateTip</td>
                    <td>Second index finger joint</td>
                </tr>
                <tr>
                    <td>9</td>
                    <td>handIndexFingerTip</td>
                    <td>Tip of index finger</td>
                </tr>
                <!-- Middle Finger -->
                <tr>
                    <td>10</td>
                    <td>handMiddleFingerMetacarpal</td>
                    <td>Base of middle finger in palm</td>
                </tr>
                <tr>
                    <td>11</td>
                    <td>handMiddleFingerKnuckle</td>
                    <td>Middle finger knuckle</td>
                </tr>
                <tr>
                    <td>12</td>
                    <td>handMiddleFingerIntermediateBase</td>
                    <td>First middle finger joint</td>
                </tr>
                <tr>
                    <td>13</td>
                    <td>handMiddleFingerIntermediateTip</td>
                    <td>Second middle finger joint</td>
                </tr>
                <tr>
                    <td>14</td>
                    <td>handMiddleFingerTip</td>
                    <td>Tip of middle finger</td>
                </tr>
                <!-- Ring Finger -->
                <tr>
                    <td>15</td>
                    <td>handRingFingerMetacarpal</td>
                    <td>Base of ring finger in palm</td>
                </tr>
                <tr>
                    <td>16</td>
                    <td>handRingFingerKnuckle</td>
                    <td>Ring finger knuckle</td>
                </tr>
                <tr>
                    <td>17</td>
                    <td>handRingFingerIntermediateBase</td>
                    <td>First ring finger joint</td>
                </tr>
                <tr>
                    <td>18</td>
                    <td>handRingFingerIntermediateTip</td>
                    <td>Second ring finger joint</td>
                </tr>
                <tr>
                    <td>19</td>
                    <td>handRingFingerTip</td>
                    <td>Tip of ring finger</td>
                </tr>
                <!-- Little Finger -->
                <tr>
                    <td>20</td>
                    <td>handLittleFingerMetacarpal</td>
                    <td>Base of little finger in palm</td>
                </tr>
                <tr>
                    <td>21</td>
                    <td>handLittleFingerKnuckle</td>
                    <td>Little finger knuckle</td>
                </tr>
                <tr>
                    <td>22</td>
                    <td>handLittleFingerIntermediateBase</td>
                    <td>First little finger joint</td>
                </tr>
                <tr>
                    <td>23</td>
                    <td>handLittleFingerIntermediateTip</td>
                    <td>Second little finger joint</td>
                </tr>
                <tr>
                    <td>24</td>
                    <td>handLittleFingerTip</td>
                    <td>Tip of little finger</td>
                </tr>
                <!-- Forearm -->
                <tr>
                    <td>25</td>
                    <td>handForearmWrist</td>
                    <td>Forearm point near wrist</td>
                </tr>
                <tr>
                    <td>26</td>
                    <td>handForearmArm</td>
                    <td>Forearm point near elbow</td>
                </tr>
            </table>
        </div>

        <div class="endpoint">
            <h2>API Endpoints</h2>
            
            <h3>1. Health Check</h3>
            <pre>GET /health</pre>
            <p>Returns server status and configuration.</p>
            
            <h3>2. Hand Validation</h3>
            <pre>POST /validate</pre>
            <p>Validates hand data and performs IK processing if enabled.</p>
            
            <h4>Example Request:</h4>
            <pre>
curl -X POST http://192.168.154.196:5001/validate \\
    -H "Content-Type: application/json" \\
    -d '{
    "hands": {
        "left_hand": {
            "points": [
                {"id": 0, "name": "handWrist", "x": 0.1, "y": 0.2, "z": 0.3},
                {"id": 1, "name": "handThumbKnuckle", "x": 0.15, "y": 0.25, "z": 0.35},
                {"id": 2, "name": "handThumbIntermediateBase", "x": 0.2, "y": 0.3, "z": 0.4},
                {"id": 3, "name": "handThumbIntermediateTip", "x": 0.25, "y": 0.35, "z": 0.45},
                {"id": 4, "name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5}
            ]
        }
    }
}'</pre>
        </div>
    </div>
</body>
</html>
""" 