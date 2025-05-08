using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace RecipeSearchApp
{
    public partial class MainWindow : Window
    {
        private List<Recipe> recipes;

        public MainWindow()
        {
            InitializeComponent();
        }

        private async void buttonSearch_Click(object sender, RoutedEventArgs e)
        {
            string searchText = textBoxSearch.Text.ToLower();

            RecipeReader recipeReader = new RecipeReader();
            var filteredRecipes = await recipeReader.GetRecipeAsync(searchText);
            recipes = filteredRecipes.ToList();

            listBoxResults.Items.Clear();
            foreach (var recipe in filteredRecipes)
            {
                listBoxResults.Items.Add(recipe.Title);
            }

            if (!filteredRecipes.Any())
            {
                MessageBox.Show("No results found.");
            }
        }

        private void listBoxResults_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (listBoxResults.SelectedItem != null)
            {
                string selectedRecipeName = listBoxResults.SelectedItem.ToString();
                var selectedRecipe = recipes.FirstOrDefault(r => r.Title == selectedRecipeName);

                if (selectedRecipe != null)
                {
                    var detailsWindow = new RecipeDetailsWindow(selectedRecipe);
                    detailsWindow.Show();
                }
            }
        }
    }
}