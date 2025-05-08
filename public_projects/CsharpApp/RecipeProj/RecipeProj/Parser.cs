using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using RecipeSearchApp;

namespace RecipeSearchApp
{
    internal class Parser : IRecipeParser
    {
        private static readonly Dictionary<string, string> ingredientAbreviations = new Dictionary<string, string>()
        {
            { " tb ", " tablespoon " },
            { " c ", " cup " },
            { " cn ", " can " },
            { " tsp ", " teaspoon " },
            { " ts ", " teaspoon " },
            { " pt ", " pint " },
            { " lb ", " pound " },
            { " oz ", " ounce " }
        };

        public void Parse(Recipe recipe)
        {
            if (recipe == null) throw new ArgumentNullException("Recipe is null.");
            if (string.IsNullOrWhiteSpace(recipe.Ingredients) || string.IsNullOrWhiteSpace(recipe.Instructions)) throw new ArgumentException("Ingredients or Instructions can't be empty");

            // Ingredients

            string ingredients = recipe.Ingredients;

            foreach (var abbreviation in ingredientAbreviations)
            {
                ingredients = ingredients.Replace(abbreviation.Key, abbreviation.Value);
            }

            string[] ingredientSentences = ingredients.Split(new[] { '|', '.' });
            string formattedIngredients = "";

            foreach (string sentence in ingredientSentences)
            {
                if (!string.IsNullOrWhiteSpace(sentence))
                {
                    formattedIngredients += $"-> {sentence.Trim()}\n";
                }
            }
            recipe.Ingredients = formattedIngredients;

            // Instructions

            string[] instructionsSentences = recipe.Instructions.Split('.');
            string formattedInstructions = "";

            for (int i = 0; i < instructionsSentences.Length; i++)
            {
                if (!string.IsNullOrWhiteSpace(instructionsSentences[i]))
                {
                    formattedInstructions += $"{i + 1}- {instructionsSentences[i].Trim()}.\n";
                }
            }

            recipe.Instructions = formattedInstructions;
        }
    }
}
