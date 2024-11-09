
## NPM (Node Package Manager)

### Initializing a New Project

- **Command:**
  ```bash
  npm init
  ```
- **Description:** Creates a `package.json` file in the current directory, which contains metadata about the project and its dependencies. Use `npm init -y` to skip prompts and create a default `package.json`.

### Installing Packages
- **Command:**
  ```bash
  npm install <package-name>
  ```
- **Description:** Installs the specified package and adds it to the `dependencies` section of the `package.json` file. Use `--save-dev` to install as a development dependency.
  - **Example:**
    ```bash
    npm install express
    ```

### Running the Application
- **Command:**
  ```bash
  node app.js
  ```
- **Description:** Starts the Node.js application defined in `app.js`. Ensure your Express server code is in this file.

