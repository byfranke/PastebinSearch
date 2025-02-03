# Pastebin Search Tool

A simple Bash script to search for terms on Pastebin using popular search engines like Google, Bing, DuckDuckGo, and Yahoo.  
This tool automates the process of opening browser tabs with search results, making it easier to investigate leaked data or specific content on Pastebin.

## Features

- **Multi-Search Engine Support** – Searches Pastebin using **Google, Bing, DuckDuckGo, and Yahoo**.
- **Customizable Browser** – Allows you to specify your preferred browser (e.g., **Firefox, Google Chrome**).
- **URL Encoding** – Automatically replaces spaces in search terms with `+` for proper URL encoding.
- **Error Handling** – Provides clear error messages if the browser fails to open or is not found.
- **Timeout Support** – Ensures the script doesn’t hang if the browser takes too long to open.

## Usage

### Basic Usage

1. Clone the repository or download the script.

   ```bash
   git clone https://github.com/byfranke/PastebinSearch
   ```

2. Make the script executable:

   ```bash
   chmod +x PastebinSearch
   ```

3. Run the script with your search terms:

   ```bash
   ./PastebinSearch search_term1 search_term2
   ```

### Example

To search for **social_security_number** and **John** on Pastebin:

```bash
./PastebinSearch social_security_number John
```

### Using a Different Browser

You can specify a browser as the **first argument**. For example, to use **Google Chrome**:

```bash
./PastebinSearch google-chrome password
```

## Requirements

- **Bash** – The script is written in **Bash** and should work on most **Unix-like systems**.
- **A Web Browser** – Firefox is the **default browser**, but you can use any browser installed on your system (e.g., **Google Chrome, Brave**).

## How It Works

1. The script checks if search terms are provided. If not, it displays a **usage message** and exits.
2. It verifies if the **specified browser** is installed. If not, it shows an **error** and exits.
3. Spaces in the search terms are replaced with **`+`** to ensure proper **URL encoding**.
4. The script opens browser tabs with **search results** from Google, Bing, DuckDuckGo, and Yahoo, all **filtered** to show results from `pastebin.com`.

## Error Handling

- If the **browser fails to open** (e.g., due to incorrect configuration or missing installation), the script **displays an error message** and exits.
- If **no search terms** are provided, the script **shows a usage example** and exits.

## Customization

- **Add More Search Engines** – You can easily add more search engines by defining their URLs and calling the `search_pastebin` function.
- **Change Default Browser** – Modify the `SEARCH` variable at the top of the script to set your preferred **default browser**.

## Example Output

```bash
$ ./PastebinSearch social_security_number John
Searching on Pastebin...
```

This will **open four browser tabs** with search results for **social_security_number** and **John** on Pastebin, using **Google, Bing, DuckDuckGo, and Yahoo**.

# Disclaimer
This tool is designed for educational and testing purposes only. The creator strictly discourages and disclaims any responsibility for its use in unauthorized or malicious activities. Always obtain explicit permission before deploying this tool in any environment.

# Donations

If you find these tools useful and would like to support ongoing development and maintenance, please consider making a donation. Your contribution helps ensure that these tools are regularly updated and improved, benefiting the cybersecurity community. Any amount is greatly appreciated and will make a significant difference in supporting this project. Thank you for considering supporting this work!

**Address Bitcoin:** 
```bash
bc1qkdh3eqpj87q5hlhc7pvm025hmsd9zp2kadxf76
```
