using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RecipeSearchApp
{
    internal interface IRecipeParser
    {
        void Parse(Recipe recipe);
    }
}
