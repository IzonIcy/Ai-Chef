import Foundation
import Combine

class PythonBridge {
    static let shared = PythonBridge()
    
    private lazy var projectRoot: String = {
        let filePath = URL(fileURLWithPath: #filePath)
        return filePath.deletingLastPathComponent().deletingLastPathComponent().path
    }()

    private lazy var pythonScript: String = {
        return URL(fileURLWithPath: projectRoot).appendingPathComponent("app_bridge.py").path
    }()
    
    /// Find recipes based on ingredients
    func findRecipes(ingredients: [String], completion: @escaping (Result<[[String: Any]], Error>) -> Void) {
        let ingredientsJSON = try! JSONSerialization.data(withJSONObject: ingredients)
        let ingredientsString = String(data: ingredientsJSON, encoding: .utf8) ?? "[]"
        
        executeCommand("find_recipes", arguments: [ingredientsString]) { result in
            switch result {
            case .success(let data):
                if let recipes = data["recipes"] as? [[String: Any]] {
                    completion(.success(recipes))
                } else {
                    completion(.success([]))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Generate a recipe with AI
    func generateRecipe(prompt: String, completion: @escaping (Result<[String: Any], Error>) -> Void) {
        executeCommand("generate_recipe", arguments: [prompt]) { result in
            switch result {
            case .success(let data):
                if let recipe = data["recipe"] as? [String: Any] {
                    completion(.success(recipe))
                } else {
                    completion(.success([:]))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Get cooking tips for a recipe
    func getCookingTips(recipeName: String, completion: @escaping (Result<[String], Error>) -> Void) {
        executeCommand("get_tips", arguments: [recipeName]) { result in
            switch result {
            case .success(let data):
                if let tips = data["tips"] as? [String] {
                    completion(.success(tips))
                } else if let tipsText = data["tips"] as? String {
                    let lines = tipsText
                        .split(separator: "\n")
                        .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
                        .filter { !$0.isEmpty }
                    completion(.success(lines))
                } else if let tipsText = data["tips_text"] as? String {
                    let lines = tipsText
                        .split(separator: "\n")
                        .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
                        .filter { !$0.isEmpty }
                    completion(.success(lines))
                } else {
                    completion(.success([]))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Get all recipes in the database
    func getAllRecipes(completion: @escaping (Result<[[String: Any]], Error>) -> Void) {
        executeCommand("get_all_recipes", arguments: []) { result in
            switch result {
            case .success(let data):
                if let recipes = data["recipes"] as? [[String: Any]] {
                    completion(.success(recipes))
                } else {
                    completion(.success([]))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Private Methods
    
    private func executeCommand(_ command: String, arguments: [String], completion: @escaping (Result<[String: Any], Error>) -> Void) {
        let task = Process()
        task.executableURL = URL(fileURLWithPath: resolvePythonExecutable())
        
        var args = [pythonScript, command]
        args.append(contentsOf: arguments)
        task.arguments = args
        
        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe
        
        DispatchQueue.global(qos: .background).async {
            do {
                try task.run()
                task.waitUntilExit()
                
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                if let jsonString = String(data: data, encoding: .utf8),
                   let jsonData = jsonString.data(using: .utf8),
                   let result = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
                    DispatchQueue.main.async {
                        completion(.success(result))
                    }
                } else {
                    throw NSError(domain: "PythonBridge", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid JSON response"])
                }
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
            }
        }
    }

    private func resolvePythonExecutable() -> String {
        let fileManager = FileManager.default
        let venvPython = URL(fileURLWithPath: projectRoot).appendingPathComponent(".venv/bin/python").path

        if fileManager.fileExists(atPath: venvPython) {
            return venvPython
        }

        if fileManager.fileExists(atPath: "/usr/bin/python3") {
            return "/usr/bin/python3"
        }

        return "python3"
    }
}

enum PythonBridgeError: Error {
    case invalidResponse
    case executionFailed(String)
}
