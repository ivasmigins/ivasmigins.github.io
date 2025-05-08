using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RecipeSearchApp
{
    public class Recipe
    {
        public string Title { get; set; } = string.Empty;
        public string Ingredients { get; set; } = string.Empty;
        public string Servings { get; set; } = string.Empty;
        public string Instructions { get; set; } = string.Empty;
        public string Fats { get; set; } = string.Empty;
        public string Carbohydrates { get; set; } = string.Empty;
        public string Fiber { get; set; } = string.Empty;

    }
}
