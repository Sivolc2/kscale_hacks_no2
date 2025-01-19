import Foundation

// MARK: - Data Structures
struct HandPoint: Codable {
    let id: Int
    let name: String
    let x: Double
    let y: Double
    let z: Double
}

struct Hand: Codable {
    let points: [HandPoint]
}

struct HandData: Codable {
    let hands: [String: Hand]
}

// MARK: - Response Structures
struct ValidationResult: Codable {
    let isValid: Bool
    let violations: [String]
    let ikResults: IKResults?
    
    enum CodingKeys: String, CodingKey {
        case isValid = "is_valid"
        case violations
        case ikResults = "ik_results"
    }
}

struct IKResults: Codable {
    let thumb: [Double]?
    let index: [Double]?
    let middle: [Double]?
    let ring: [Double]?
    let little: [Double]?
    let plotPath: String?
    
    enum CodingKeys: String, CodingKey {
        case thumb, index, middle, ring, little
        case plotPath = "plot_path"
    }
}

struct ValidationResponse: Codable {
    let validationResults: [String: ValidationResult]
    let overallValid: Bool
    
    enum CodingKeys: String, CodingKey {
        case validationResults = "validation_results"
        case overallValid = "overall_valid"
    }
}

// MARK: - Hand IK Client
class HandIKClient {
    private let baseURL: String
    private let session: URLSession
    
    init(baseURL: String = "http://192.168.154.196:5001") {
        self.baseURL = baseURL
        
        // Create URL session configuration with increased timeout
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Health Check
    func checkHealth() async throws -> Bool {
        guard let url = URL(string: "\(baseURL)/health") else {
            throw URLError(.badURL)
        }
        
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        return json?["status"] as? String == "healthy"
    }
    
    // MARK: - Validate Hand
    func validateHand(points: [HandPoint], sourceFile: String? = nil) async throws -> ValidationResponse {
        guard let url = URL(string: "\(baseURL)/validate") else {
            throw URLError(.badURL)
        }
        
        // Create request
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let sourceFile = sourceFile {
            request.setValue(sourceFile, forHTTPHeaderField: "X-Source-File")
        }
        
        // Create hand data
        let handData = HandData(hands: ["left_hand": Hand(points: points)])
        request.httpBody = try JSONEncoder().encode(handData)
        
        // Send request
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard httpResponse.statusCode == 200 else {
            if let errorJson = try? JSONSerialization.jsonObject(with: data) as? [String: String],
               let errorMessage = errorJson["error"] {
                throw NSError(domain: "HandIKError", code: httpResponse.statusCode, userInfo: [
                    NSLocalizedDescriptionKey: errorMessage
                ])
            }
            throw URLError(.badServerResponse)
        }
        
        return try JSONDecoder().decode(ValidationResponse.self, from: data)
    }
}

// MARK: - Example Usage
extension HandIKClient {
    static func example() async {
        let client = HandIKClient()
        
        do {
            // Check server health
            let isHealthy = try await client.checkHealth()
            print("Server health:", isHealthy ? "Healthy" : "Unhealthy")
            
            // Example hand points
            let points = [
                HandPoint(id: 0, name: "handWrist", x: 0.1, y: 0.2, z: 0.3),
                HandPoint(id: 1, name: "handThumbKnuckle", x: 0.15, y: 0.25, z: 0.35),
                HandPoint(id: 2, name: "handThumbIntermediateBase", x: 0.2, y: 0.3, z: 0.4),
                HandPoint(id: 3, name: "handThumbIntermediateTip", x: 0.25, y: 0.35, z: 0.45),
                HandPoint(id: 4, name: "handThumbTip", x: 0.3, y: 0.4, z: 0.5)
            ]
            
            // Validate hand
            let result = try await client.validateHand(points: points, sourceFile: "example.json")
            
            // Print results
            print("\nValidation Results:")
            print("Overall valid:", result.overallValid)
            
            if let leftHand = result.validationResults["left_hand"] {
                print("\nLeft Hand:")
                print("Valid:", leftHand.isValid)
                print("Violations:", leftHand.violations)
                
                if let ikResults = leftHand.ikResults {
                    print("\nIK Results:")
                    if let thumb = ikResults.thumb {
                        print("Thumb angles:", thumb)
                    }
                    if let plotPath = ikResults.plotPath {
                        print("Plot saved to:", plotPath)
                    }
                }
            }
            
        } catch {
            print("Error:", error.localizedDescription)
        }
    }
}

// MARK: - Run Example
#if DEBUG
@main
struct HandIKExample {
    static func main() async {
        await HandIKClient.example()
    }
}
#endif 