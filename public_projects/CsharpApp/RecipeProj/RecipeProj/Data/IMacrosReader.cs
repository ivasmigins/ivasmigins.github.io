using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using RecipeSearchApp;

namespace RecipeSearchApp
{
    internal interface IMacrosReader
    {
        Task GetMacrosAsync(Recipe recipe);
    }
}
