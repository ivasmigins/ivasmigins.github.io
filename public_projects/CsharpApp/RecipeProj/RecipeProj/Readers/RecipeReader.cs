using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace RecipeSearchApp
{
    class RecipeReader : IRecipeReader
    {
        private Parser parser = new Parser();
        public async Task<List<Recipe>> GetRecipeAsync(string query)
        {
            var recipeBaseURL = "https://api.api-ninjas.com/v1/recipe?query=";
            var recipeUrl = recipeBaseURL + query;

            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("X-Api-Key", "ZJ9e8Q1ulpJKegxkbzi6yg==hoEohU2oETkmPWyK");

                try
                {
                    var response = await client.GetAsync(recipeUrl);
                    response.EnsureSuccessStatusCode();

                    var responseContent = await response.Content.ReadAsStringAsync();

                    List<Recipe>? recipes = JsonConvert.DeserializeObject<List<Recipe>>(responseContent);

                    MacrosReader macrosReader = new MacrosReader();

                    if (recipes != null)
                    {
                        recipes.ForEach(parser.Parse);
                        var macrosTasks = recipes.Select(macrosReader.GetMacrosAsync);
                        await Task.WhenAll(macrosTasks);
                    }

                    return recipes ?? new List<Recipe>();
                }
                catch (HttpRequestException e)
                {
                    Console.WriteLine($"Request error: {e.Message}");
                    return new List<Recipe>();
                }
                catch (JsonException e)
                {
                    Console.WriteLine($"Deserialization error: {e.Message}");
                    return new List<Recipe>();
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error: {e.Message}");
                    return new List<Recipe>();
                }
            }
        }
    }
}
