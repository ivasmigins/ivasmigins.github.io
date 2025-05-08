using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using RecipeSearchApp;

namespace RecipeSearchApp
{
    internal interface IRecipeReader
    {
        Task<List<Recipe>> GetRecipeAsync(string query);
    }
}
