using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace RecipeSearchApp
{
    public class Ingredient
    {
        [JsonProperty("fat_total_g")]
        public float Fat { get; set; }
        [JsonProperty("carbohydrates_total_g")]
        public float Carbs { get; set; }
        [JsonProperty("fiber_g")]
        public float Fiber { get; set; }
    }
}
