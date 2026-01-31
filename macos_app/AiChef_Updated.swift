import SwiftUI

@main
struct AiChefApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            FindRecipesView()
                .tabItem {
                    Label("Find Recipes", systemImage: "book.fill")
                }
                .tag(0)
            
            AIGeneratorView()
                .tabItem {
                    Label("Generate", systemImage: "sparkles")
                }
                .tag(1)
            
            MealPlannerView()
                .tabItem {
                    Label("Meal Plan", systemImage: "calendar")
                }
                .tag(2)
            
            SavedRecipesView()
                .tabItem {
                    Label("Saved", systemImage: "heart.fill")
                }
                .tag(3)
        }
        .frame(minWidth: 1000, minHeight: 700)
    }
}

// MARK: - Find Recipes View

struct FindRecipesView: View {
    @State private var ingredients = ""
    @State private var recipes: [RecipeModel] = []
    @State private var isLoading = false
    @State private var selectedRecipe: RecipeModel?
    @State private var errorMessage = ""
    
    var body: some View {
        VStack(spacing: 20) {
            // Search Section
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
                    .font(.body)
                
                HStack(spacing: 10) {
                    Button(action: searchRecipes) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                            }
                            Text(isLoading ? "Searching..." : "Search Recipes")
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
            
            // Results Section
            if !errorMessage.isEmpty {
                HStack {
                    Image(systemName: "exclamationmark.circle")
                    Text(errorMessage)
                    Spacer()
                    Button(action: { errorMessage = "" }) {
                        Image(systemName: "xmark")
                    }
                }
                .padding()
                .background(Color.red.opacity(0.1))
                .foregroundColor(.red)
                .cornerRadius(8)
            }
            
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
                List(recipes, id: \.id) { recipe in
                    RecipeRow(recipe: recipe)
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
        errorMessage = ""
        
        let ingredientList = ingredients
            .split(separator: ",")
            .map { String($0).trimmingCharacters(in: .whitespaces) }
        
        PythonBridge.shared.findRecipes(ingredients: ingredientList) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let recipesData):
                    recipes = recipesData.compactMap { RecipeModel(from: $0) }
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    recipes = []
                }
                isLoading = false
            }
        }
    }
}

// MARK: - AI Generator View

struct AIGeneratorView: View {
    @State private var prompt = ""
    @State private var generatedRecipe: RecipeModel?
    @State private var isLoading = false
    @State private var errorMessage = ""
    
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
                    .font(.body)
                
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
            
            if !errorMessage.isEmpty {
                HStack {
                    Image(systemName: "exclamationmark.circle")
                    Text(errorMessage)
                    Spacer()
                }
                .padding()
                .background(Color.red.opacity(0.1))
                .foregroundColor(.red)
                .cornerRadius(8)
            }
            
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
        errorMessage = ""
        
        PythonBridge.shared.generateRecipe(prompt: prompt) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let recipeData):
                    generatedRecipe = RecipeModel(from: recipeData)
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
                isLoading = false
            }
        }
    }
}

// MARK: - Meal Planner View

struct MealPlannerView: View {
    @State private var mealPlan: [String: String] = [:]
    @State private var selectedDay = "Monday"
    @State private var mealInput = ""
    @State private var mealType = "Breakfast"
    
    let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    let mealTypes = ["Breakfast", "Lunch", "Dinner", "Snack"]
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Weekly Meal Planner")
                .font(.title2)
                .fontWeight(.bold)
            
            VStack(spacing: 12) {
                HStack(spacing: 15) {
                    VStack(alignment: .leading) {
                        Text("Day").font(.caption).foregroundColor(.gray)
                        Picker("Day", selection: $selectedDay) {
                            ForEach(days, id: \.self) { day in
                                Text(day).tag(day)
                            }
                        }
                        .pickerStyle(.segmented)
                    }
                }
                
                HStack(spacing: 15) {
                    VStack(alignment: .leading) {
                        Text("Meal Type").font(.caption).foregroundColor(.gray)
                        Picker("Type", selection: $mealType) {
                            ForEach(mealTypes, id: \.self) { type in
                                Text(type).tag(type)
                            }
                        }
                        .pickerStyle(.segmented)
                    }
                }
                
                HStack(spacing: 10) {
                    TextField("Enter meal", text: $mealInput)
                        .textFieldStyle(.roundedBorder)
                    
                    Button(action: addMeal) {
                        Text("Add")
                            .padding(.horizontal, 15)
                            .padding(.vertical, 8)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(6)
                    }
                    .disabled(mealInput.isEmpty)
                }
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(12)
            
            Text("Your Meal Plan")
                .font(.headline)
            
            List(days, id: \.self) { day in
                VStack(alignment: .leading, spacing: 8) {
                    Text(day)
                        .fontWeight(.semibold)
                    
                    if let meal = mealPlan[day] {
                        HStack {
                            Text(meal)
                                .foregroundColor(.blue)
                            Spacer()
                            Button(action: { mealPlan.removeValue(forKey: day) }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(.red)
                            }
                        }
                    } else {
                        Text("No meal planned")
                            .foregroundColor(.gray)
                            .italic()
                    }
                }
            }
            
            Spacer()
        }
        .padding()
    }
    
    private func addMeal() {
        let key = "\(selectedDay)-\(mealType)"
        mealPlan[key] = mealInput
        mealInput = ""
    }
}

// MARK: - Saved Recipes View

struct SavedRecipesView: View {
    @State private var savedRecipes: [RecipeModel] = []
    @State private var selectedRecipe: RecipeModel?
    @State private var searchText = ""
    
    var filteredRecipes: [RecipeModel] {
        if searchText.isEmpty {
            return savedRecipes
        }
        return savedRecipes.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Saved Recipes")
                .font(.title2)
                .fontWeight(.bold)
            
            SearchBar(text: $searchText)
                .padding(.horizontal)
            
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
                List(filteredRecipes, id: \.id) { recipe in
                    RecipeRow(recipe: recipe)
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
        .onAppear {
            loadSavedRecipes()
        }
    }
    
    private func loadSavedRecipes() {
        // Load from UserDefaults or local storage
        if let data = UserDefaults.standard.data(forKey: "savedRecipes"),
           let recipes = try? JSONDecoder().decode([RecipeModel].self, from: data) {
            savedRecipes = recipes
        }
    }
}

// MARK: - Recipe Detail View

struct RecipeDetailView: View {
    let recipe: RecipeModel
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
                        .font(.title2)
                }
            }
            
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Info Section
                    HStack(spacing: 20) {
                        VStack(spacing: 8) {
                            Image(systemName: "clock")
                                .font(.title3)
                            Text(recipe.cookTime)
                                .font(.caption)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        
                        VStack(spacing: 8) {
                            Image(systemName: "chart.bar")
                                .font(.title3)
                            Text(recipe.difficulty)
                                .font(.caption)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        
                        Spacer()
                    }
                    
                    Divider()
                    
                    // Ingredients
                    VStack(alignment: .leading, spacing: 12) {
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
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Instructions")
                            .font(.headline)
                        ForEach(Array(recipe.instructions.enumerated()), id: \.offset) { index, instruction in
                            HStack(alignment: .top, spacing: 12) {
                                Text("\(index + 1).")
                                    .fontWeight(.semibold)
                                    .frame(width: 20, alignment: .leading)
                                Text(instruction)
                            }
                        }
                    }
                    
                    if !recipe.tags.isEmpty {
                        Divider()
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Tags")
                                .font(.headline)
                            FlowLayout(items: recipe.tags) { tag in
                                Text(tag)
                                    .font(.caption)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.blue.opacity(0.2))
                                    .foregroundColor(.blue)
                                    .cornerRadius(16)
                            }
                        }
                    }
                }
            }
            
            HStack(spacing: 10) {
                Button(action: saveRecipe) {
                    HStack {
                        Image(systemName: isSaved ? "heart.fill" : "heart")
                        Text(isSaved ? "Saved" : "Save")
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
    
    private func saveRecipe() {
        isSaved.toggle()
        // Save to UserDefaults
        var saved: [RecipeModel] = []
        if let data = UserDefaults.standard.data(forKey: "savedRecipes"),
           let decoded = try? JSONDecoder().decode([RecipeModel].self, from: data) {
            saved = decoded
        }
        
        if isSaved && !saved.contains(where: { $0.id == recipe.id }) {
            saved.append(recipe)
        } else if !isSaved {
            saved.removeAll { $0.id == recipe.id }
        }
        
        if let encoded = try? JSONEncoder().encode(saved) {
            UserDefaults.standard.set(encoded, forKey: "savedRecipes")
        }
    }
}

// MARK: - Helper Views

struct RecipeRow: View {
    let recipe: RecipeModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(recipe.name)
                .font(.headline)
            HStack(spacing: 15) {
                Label(recipe.cookTime, systemImage: "clock")
                Label(recipe.difficulty, systemImage: "chart.bar")
                if !recipe.tags.isEmpty {
                    Text(recipe.tags.prefix(2).joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            .font(.caption)
            .foregroundColor(.gray)
        }
    }
}

struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("Search recipes", text: $text)
                .textFieldStyle(.roundedBorder)
            
            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
    }
}

struct FlowLayout<T>: View {
    let items: [T]
    let content: (T) -> AnyView
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            var row: [T] = []
            
            ForEach(0..<items.count, id: \.self) { index in
                if index > 0 && index % 3 == 0 {
                    HStack(spacing: 8) {
                        ForEach(0..<row.count, id: \.self) { i in
                            content(row[i])
                        }
                        Spacer()
                    }
                    .onAppear {
                        row = []
                    }
                }
            }
            
            HStack(spacing: 8) {
                ForEach(0..<items.count, id: \.self) { index in
                    content(items[index])
                }
                Spacer()
            }
        }
    }
}

// MARK: - Models

struct RecipeModel: Identifiable, Codable {
    let id = UUID()
    let name: String
    let cookTime: String
    let difficulty: String
    let ingredients: [String]
    let instructions: [String]
    let tags: [String]
    
    init(
        name: String,
        cookTime: String,
        difficulty: String,
        ingredients: [String],
        instructions: [String],
        tags: [String]
    ) {
        self.name = name
        self.cookTime = cookTime
        self.difficulty = difficulty
        self.ingredients = ingredients
        self.instructions = instructions
        self.tags = tags
    }
    
    init?(from dictionary: [String: Any]) {
        guard let name = dictionary["name"] as? String else { return nil }
        
        self.name = name
        self.cookTime = dictionary["cook_time"] as? String ?? "Unknown"
        self.difficulty = dictionary["difficulty"] as? String ?? "Unknown"
        self.ingredients = dictionary["ingredients"] as? [String] ?? []
        self.instructions = dictionary["instructions"] as? [String] ?? []
        self.tags = dictionary["tags"] as? [String] ?? []
    }
    
    enum CodingKeys: String, CodingKey {
        case name, cookTime, difficulty, ingredients, instructions, tags
    }
}

#Preview {
    ContentView()
}
