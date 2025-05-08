using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json;
using RecipeSearchApp;

namespace RecipeSearchApp
{
    internal class MacrosReader : IMacrosReader
    {
        private string FormatIngredients(string givenIngredients)
        {
            List<string> ingredients = new List<string>();
            Regex regex = new Regex(@"->(.+?)(?:\r\n|\r|\n|$)");

            foreach (Match match in regex.Matches(givenIngredients))
            {
                string item = match.Groups[1].Value.Trim();
                ingredients.Add(item);
            }
            string query = string.Join(" and ", ingredients);

            Console.WriteLine(query);

            return query;
        }

        public async Task GetMacrosAsync(Recipe recipe)
        {
            string query = FormatIngredients(recipe.Ingredients);

            if (string.IsNullOrEmpty(query))
            {
                Console.WriteLine("Could not format ingredients to get macros.");
                return;
            }

            var macrosBaseURL = "https://api.api-ninjas.com/v1/nutrition?query=";
            var macrosUrl = macrosBaseURL + query;

            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("X-Api-Key", "ZJ9e8Q1ulpJKegxkbzi6yg==hoEohU2oETkmPWyK");

                try
                {
                    var response = await client.GetAsync(macrosUrl);
                    response.EnsureSuccessStatusCode();

                    var responseContent = await response.Content.ReadAsStringAsync();

                    List<Ingredient>? ingredients = JsonConvert.DeserializeObject<List<Ingredient>>(responseContent);

                    if (ingredients != null)
                    {
                        recipe.Fats = ingredients.Sum(ingredient => ingredient.Fat).ToString("0.00") + " g";
                        recipe.Fiber = ingredients.Sum(ingredient => ingredient.Fiber).ToString("0.00") + " g";
                        recipe.Carbohydrates = ingredients.Sum(ingredient => ingredient.Carbs).ToString("0.00") + " g";
                    }
                }
                catch (HttpRequestException e)
                {
                    Console.WriteLine($"Request error: {e.Message}");
                    return;
                }
                catch (JsonException e)
                {
                    Console.WriteLine($"Deserialization error: {e.Message}");
                    return;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error: {e.Message}");
                    return;
                }
            }
        }
    }
}
