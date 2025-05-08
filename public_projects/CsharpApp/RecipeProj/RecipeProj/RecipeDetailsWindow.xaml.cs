using System.Windows;


namespace RecipeSearchApp
{
    public partial class RecipeDetailsWindow : Window
    {
        public RecipeDetailsWindow(Recipe recipe)
        {
            InitializeComponent();
            textBlockRecipeName.Text = recipe.Title;
            textBoxIngredients.Text = recipe.Ingredients;
            textBoxInstructions.Text = $"{recipe.Servings}\n" + recipe.Instructions;
            textBoxFats.Text = recipe.Fats;
            textBoxCarbohydrates.Text = recipe.Carbohydrates;
            textBoxFiber.Text = recipe.Fiber;
        }
    }
}