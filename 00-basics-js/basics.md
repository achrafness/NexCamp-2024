# JavaScript Basics 

## Variables
- **Declare variables**
  ```javascript
  const age = 30; 
  let name = "John"; 
  ```

## Control Structures
- **Conditional Statements:**
  ```javascript
  if (condition) {
      // code
  } else if (anotherCondition) {
      // code
  } else {
      // code
  }
  ```

- **Switch Statement:**
  ```javascript
  switch (expression) {
      case value1:
          // code
          break;
      case value2:
          // code
          break;
      default:
          // code
  }
  ```

- **Loops:**
  - **For Loop:**
    ```javascript
    for (let i = 0; i < 10; i++) {
        // code
    }
    ```
  - **While Loop:**
    ```javascript
    while (condition) {
        // code
    }
    ```


## Functions
- **Function Declaration:**
  ```javascript
  function functionName(params) {
      // code
  }
  ```

- **Function Expression:**
  ```javascript
  const functionName = function(params) {
      // code
  };
  ```

- **Arrow Function:**
  ```javascript
  const functionName = (params) => {
      // code
  };
  ```

## Objects
- **Creating an Object:**
  ```javascript
  const person = {
      name: "John",
      age: 30
  };
  ```

- **Accessing Object Properties:**
  ```javascript
  console.log(person.name); // Dot notation
  console.log(person["age"]); // Bracket notation
  ```

## Arrays
- **Creating an Array:**
  ```javascript
  const fruits = ["apple", "banana", "cherry"];
  ```

- **Array Methods:**
  - `push()`: Add to end
  - `pop()`: Remove from end
  - `shift()`: Remove from start
  - `unshift()`: Add to start

## Higher Order Functions
- **Definition**: Functions that can take other functions as arguments or return them as output.
  
- **Example of Higher-Order Function:**
  ```javascript
  function greet(name) {
      return `Hello, ${name}!`;
  }

  function processUserInput(callback) {
      const name = "John";
      console.log(callback(name));
  }

  processUserInput(greet); // Output: Hello, John!
  ```

- **Array Methods that are Higher-Order Functions:**
  - **`map()`:** Transforms each element in an array.
    ```javascript
    const numbers = [1, 2, 3];
    const doubled = numbers.map((num) => num * 2); // [2, 4, 6]
    ```
  
  - **`filter()`:** Filters elements based on a condition.
    ```javascript
    const evens = numbers.filter((num) => num % 2 === 0); // [2]
    ```

  - **`forEach()`:** Executes a function for each element.
    ```javascript
    numbers.forEach((num) => console.log(num)); // Outputs each number
    ```
