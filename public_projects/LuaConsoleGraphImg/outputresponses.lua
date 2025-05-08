return {
    invalid_http_request = "HTTP request failed with code:",
    error_decoding_json = "Error: Could not decode JSON data.",
    invalid_command = "Invalid command. Please type 'help' to see the list of available commands.",
    invalid_argument = "Invalid argument. Please type 'help' to see the list of available commands.",
    invalid_data = "Invalid data. Please try again.",
    invalid_date = "Invalid date format. Please try again.",
    help = "Available commands:\n\n" ..
            "help - Display this help message\n" ..
            "exit - Exit the program\n" ..
            "list - List all available devices\n" ..
            "stats <device> - Get the basic stats for a device\n" ..
            "graph <time> <attribute> <filename> <devices> - Make a graph of the desired stat. Accepted times are: \n-(last) hour, day, week\n-dates: start-end (dd/mm/yy) example: 12/09/2024-14/09/2024\n",
    welcome = "|| Welcome to the weather console application ||\n" ..
               "\nType 'help' to see the list of available commands.",
    exit = "|| Thanks for using the weather console application. ||"
}