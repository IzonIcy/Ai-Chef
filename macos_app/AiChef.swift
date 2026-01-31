import SwiftUI

@main
struct AiChefApp: App {
    @State private var pythonHelper = PythonHelper()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(pythonHelper)
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var pythonHelper: PythonHelper
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Find Recipes Tab
            FindRecipesView()
                .environmentObject(pythonHelper)
                .tabItem {
                    Label("Find Recipes", systemImage: "book.fill")
                }
                .tag(0)
            
            // AI Generator Tab
            AIGeneratorView()
                .environmentObject(pythonHelper)
                .tabItem {
                    Label("Generate", systemImage: "sparkles")
                }
                .tag(1)
            
            // Meal Planner Tab
            MealPlannerView()
                .environmentObject(pythonHelper)
                .tabItem {
                    Label("Planner", systemImage: "calendar")
                }
                .tag(2)
            
            // Saved Recipes Tab
            SavedRecipesView()
                .environmentObject(pythonHelper)
                .tabItem {
                    Label("Saved", systemImage: "heart.fill")
                }
                .tag(3)
        }
        .frame(minWidth: 900, minHeight: 700)
    }
}

struct FindRecipesView: View {
    @EnvironmentObject var pythonHelper: PythonHelper
    @State private var ingredients = ""
    @State private var recipes: [Recipe] = []
    @State private var isLoading = false
    @State private var selectedRecipe: Recipe?
    
    var body: some View {
        VStack(spacing: 20) {
            VStack(alignment: .leading, spacing: 10) {
                Text("Find Recipes by Ingredients")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Enter ingredients you have (comma-separated)")
                    .font(.caption)
                    .foregroundColor(.gray)
                
                TextEditor(text: $ingredients)
                    .frame(height: 100)
                    .border(Color.gray.opacity(0.3))
                    .cornerRadius(8)
                
                HStack(spacing: 10) {
                    Button(action: searchRecipes) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                            }
                            Text(isLoading ? "Searching..." : "Search")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                    .disabled(isLoading || ingredients.isEmpty)
                    
                    Button(action: { ingredients = "" }) {
                        Text("Clear")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.gray.opacity(0.2))
                            .cornerRadius(8)
                    }
                }
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(12)
            
            if recipes.isEmpty && !isLoading {
                VStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 40))
                        .foregroundColor(.gray)
                    Text("Enter ingredients to find recipes")
                        .foregroundColor(.gray)
                }
                .frame(maxHeight: .infinity)
            } else {
                List(recipes, id: \.name) { recipe in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(recipe.name)
                            .font(.headline)
                        HStack(spacing: 15) {
                            Label(recipe.cookTime, systemImage: "clock")
                            Label("\(recipe.difficulty)", systemImage: "chart.bar")
                            if !recipe.tags.isEmpty {
                                Text(recipe.tags.joined(separator: ", "))
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                        }
                        .font(.caption)
                        .foregroundColor(.gray)
                    }
                    .onTapGesture {
                        selectedRecipe = recipe
                    }
                }
            }
        }
        .padding()
        .sheet(item: $selectedRecipe) { recipe in
            RecipeDetailView(recipe: recipe)
        }
    }
    
    private func searchRecipes() {
        isLoading = true
        let ingredientList = ingredients
            .split(separator: ",")
            .map { String($0).trimmingCharacters(in: .whitespaces) }
        
        pythonHelper.findRecipes(ingredients: ingredientList) { result in
            DispatchQueue.main.async {
                if case .success(let foundRecipes) = result {
                    recipes = foundRecipes
                }
                isLoading = false
            }
        }
    }
}

struct AIGeneratorView: View {
    @EnvironmentObject var pythonHelper: PythonHelper
    @State private var prompt = ""
    @State private var generatedRecipe: Recipe?
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 20) {
            VStack(alignment: .leading, spacing: 10) {
                Text("Generate Custom Recipe with AI")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Describe the recipe you'd like to create")
                    .font(.caption)
                    .foregroundColor(.gray)
                
                TextEditor(text: $prompt)
                    .frame(height: 150)
                    .border(Color.gray.opacity(0.3))
                    .cornerRadius(8)
                
                Button(action: generateRecipe) {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .scaleEffect(0.8)
                        }
                        Text(isLoading ? "Generating..." : "Generate Recipe")
                            .fontWeight(.semibold)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.purple)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .disabled(isLoading || prompt.isEmpty)
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(12)
            
            if let recipe = generatedRecipe {
                RecipeDetailView(recipe: recipe)
            } else if !isLoading {
                VStack(spacing: 10) {
                    Image(systemName: "sparkles")
                        .font(.system(size: 40))
                        .foregroundColor(.purple)
                    Text("Describe what you'd like to cook")
                        .foregroundColor(.gray)
                }
                .frame(maxHeight: .infinity)
            }
            
            Spacer()
        }
        .padding()
    }
    
    private func generateRecipe() {
        isLoading = true
        pythonHelper.generateRecipe(prompt: prompt) { result in
            DispatchQueue.main.async {
                if case .success(let recipe) = result {
                    generatedRecipe = recipe
                }
                isLoading = false
            }
        }
    }
}

struct MealPlannerView: View {
    @State private var mealPlan: [String: String] = [:]
    @State private var selectedDay = "Monday"
    @State private var mealInput = ""
    
    let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Weekly Meal Planner")
                .font(.title2)
                .fontWeight(.bold)
            
            HStack(spacing: 10) {
                Picker("Day", selection: $selectedDay) {
                    ForEach(days, id: \.self) { day in
                        Text(day).tag(day)
                    }
                }
                
                TextField("Meal", text: $mealInput)
                    .textFieldStyle(.roundedBorder)
                
                Button(action: addMeal) {
                    Text("Add")
                        .padding(.horizontal)
                }
                .buttonStyle(.borderedProminent)
            }
            
            List(days, id: \.self) { day in
                HStack {
                    Text(day)
                        .fontWeight(.semibold)
                    Spacer()
                    Text(mealPlan[day] ?? "No meal planned")
                        .foregroundColor(.gray)
                }
            }
            
            Spacer()
        }
        .padding()
    }
    
    private func addMeal() {
        if !mealInput.isEmpty {
            mealPlan[selectedDay] = mealInput
            mealInput = ""
        }
    }
}

struct SavedRecipesView: View {
    @State private var savedRecipes: [Recipe] = []
    @State private var selectedRecipe: Recipe?
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Saved Recipes")
                .font(.title2)
                .fontWeight(.bold)
            
            if savedRecipes.isEmpty {
                VStack(spacing: 10) {
                    Image(systemName: "heart")
                        .font(.system(size: 40))
                        .foregroundColor(.red)
                    Text("No saved recipes yet")
                        .foregroundColor(.gray)
                    Text("Save recipes while browsing to see them here")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .frame(maxHeight: .infinity)
            } else {
                List(savedRecipes, id: \.name) { recipe in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(recipe.name)
                            .font(.headline)
                        HStack(spacing: 15) {
                            Label(recipe.cookTime, systemImage: "clock")
                            Label("\(recipe.difficulty)", systemImage: "chart.bar")
                        }
                        .font(.caption)
                        .foregroundColor(.gray)
                    }
                    .onTapGesture {
                        selectedRecipe = recipe
                    }
                }
            }
        }
        .padding()
        .sheet(item: $selectedRecipe) { recipe in
            RecipeDetailView(recipe: recipe)
        }
    }
}

struct RecipeDetailView: View {
    let recipe: Recipe
    @Environment(\.dismiss) var dismiss
    @State private var isSaved = false
    
    var body: some View {
        VStack(spacing: 20) {
            HStack {
                Text(recipe.name)
                    .font(.title)
                    .fontWeight(.bold)
                Spacer()
                Button(action: { dismiss() }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
            
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Info Section
                    HStack(spacing: 20) {
                        InfoCard(icon: "clock", label: recipe.cookTime)
                        InfoCard(icon: "chart.bar", label: recipe.difficulty)
                        Spacer()
                    }
                    
                    Divider()
                    
                    // Ingredients
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Ingredients")
                            .font(.headline)
                        ForEach(recipe.ingredients, id: \.self) { ingredient in
                            HStack {
                                Image(systemName: "checkmark.circle")
                                    .foregroundColor(.green)
                                Text(ingredient)
                            }
                        }
                    }
                    
                    Divider()
                    
                    // Instructions
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Instructions")
                            .font(.headline)
                        ForEach(Array(recipe.instructions.enumerated()), id: \.offset) { index, instruction in
                            HStack(alignment: .top, spacing: 10) {
                                Text("\(index + 1).")
                                    .fontWeight(.semibold)
                                Text(instruction)
                            }
                        }
                    }
                    
                    if !recipe.tags.isEmpty {
                        Divider()
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Tags")
                                .font(.headline)
                            FlowLayout(items: recipe.tags) { tag in
                                Text(tag)
                                    .font(.caption)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.blue.opacity(0.2))
                                    .cornerRadius(16)
                            }
                        }
                    }
                }
            }
            
            HStack(spacing: 10) {
                Button(action: { isSaved.toggle() }) {
                    HStack {
                        Image(systemName: isSaved ? "heart.fill" : "heart")
                        Text("Save")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(isSaved ? Color.red.opacity(0.2) : Color.gray.opacity(0.1))
                    .foregroundColor(isSaved ? .red : .gray)
                    .cornerRadius(8)
                }
                
                Button(action: { dismiss() }) {
                    Text("Close")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(8)
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(Color(.systemBackground))
    }
}

struct InfoCard: View {
    let icon: String
    let label: String
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title3)
            Text(label)
                .font(.caption)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
}

struct FlowLayout<T>: View {
    let items: [T]
    let content: (T) -> AnyView
    
    var body: some View {
        var rows: [[T]] = []
        var currentRow: [T] = []
        
        for item in items {
            currentRow.append(item)
            if currentRow.count >= 3 {
                rows.append(currentRow)
                currentRow = []
            }
        }
        
        if !currentRow.isEmpty {
            rows.append(currentRow)
        }
        
        return VStack(spacing: 10) {
            ForEach(0..<rows.count, id: \.self) { rowIndex in
                HStack(spacing: 10) {
                    ForEach(0..<rows[rowIndex].count, id: \.self) { itemIndex in
                        content(rows[rowIndex][itemIndex])
                        Spacer()
                    }
                }
            }
        }
    }
}

// MARK: - Models

struct Recipe: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let cookTime: String
    let difficulty: String
    let ingredients: [String]
    let instructions: [String]
    let tags: [String]
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: Recipe, rhs: Recipe) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - Python Helper

class PythonHelper: ObservableObject {
    @Published var isProcessing = false
    
    func findRecipes(ingredients: [String], completion: @escaping (Result<[Recipe], Error>) -> Void) {
        // This will call your Python backend
        let mockRecipes = [
            Recipe(
                name: "Pasta Carbonara",
                cookTime: "20 min",
                difficulty: "Easy",
                ingredients: ["Pasta", "Eggs", "Bacon", "Parmesan"],
                instructions: ["Boil pasta", "Cook bacon", "Mix eggs and cheese", "Combine all"],
                tags: ["Italian", "Quick", "Pasta"]
            ),
            Recipe(
                name: "Chicken Stir Fry",
                cookTime: "30 min",
                difficulty: "Medium",
                ingredients: ["Chicken", "Vegetables", "Soy Sauce", "Rice"],
                instructions: ["Prepare ingredients", "Heat wok", "Cook chicken", "Add vegetables"],
                tags: ["Asian", "Healthy", "Quick"]
            )
        ]
        completion(.success(mockRecipes))
    }
    
    func generateRecipe(prompt: String, completion: @escaping (Result<Recipe, Error>) -> Void) {
        let recipe = Recipe(
            name: "AI Generated: \(prompt.prefix(20))",
            cookTime: "30 min",
            difficulty: "Medium",
            ingredients: ["Ingredient 1", "Ingredient 2", "Ingredient 3"],
            instructions: ["Step 1", "Step 2", "Step 3"],
            tags: ["Generated", "Custom"]
        )
        completion(.success(recipe))
    }
}

#Preview {
    ContentView()
        .environmentObject(PythonHelper())
}
