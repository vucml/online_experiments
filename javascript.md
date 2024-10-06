# Some JavaScript Pointers

If you're seeking to learn JavaScript, I suggest the [MDN JavaScript reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference) as a good place to start. It provides tutorials at different levels of experiment ("Complete beginners", "Intermediate", "Advanced") as well as a relatively comprehensive reference of all the language's features. This along with a style guide for organizing JavaScript code like [Airbnb's](https://github.com/airbnb/javascript) should be enough -- maybe more than an enough -- to get you started.

Here we'll track mysterious language features that show up in this codebase. If you see something in the codebase that you don't understand, check here first. If it's not mentioned, maybe add an entry here or raise an issue in the github repo.

<!-- 
TODO: continue from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Indexed_collections
 -->

## Accessing Primitives vs Complex Types

<!-- notecardId: 1705316864961 -->

When you access a primitive type you work directly on its value. In other words, any changes to the value are made directly to that value (passed by value).

When you access a complex type you work on a reference to its value. In other words, a reference to the value is passed (passed by reference). Any changes to the value are made on the reference to the value, not the actual value, so any other references to the same value will see the change.

## DOM

<!-- notecardId: 1705316864965 -->

 Document Object Model. Client-side JavaScript extends the core language by supplying objects to control a browser and its Document Object Model (DOM). For example, client-side extensions allow an application to place elements on an HTML form and respond to user events such as mouse clicks, form input, and page navigation.

## Comments

<!-- notecardId: 1705316864968 -->


Javascript has two types of comments: single-line comments and multi-line comments. Single-line comments start with `//` and multi-line comments start with `/*` and end with `*/`.

## Block Scope

<!-- notecardId: 1705316864972 -->


A block is a chunk of code bounded by `{}`. A block lives in curly braces. Variables declared with `let` and `const` are block scoped. Variables declared inside a block can not be accessed from outside the block.

## Global Object

<!-- notecardId: 1705316864975 -->


lobal variables are in fact properties of the global object. In web pages the global object is `window`, so you can set and access global variables using the `window.variable` syntax. In all environments, the `globalThis` variable provides a convenient way to access the global object.

## Declarations: var

<!-- notecardId: 1705316864978 -->


JavaScript has three types of declarations: var, let, and const. Variables declared with var are scoped to the function in which they are created, or if created outside of any function, to the global object.

## Declarations: let vs const

<!-- notecardId: 1705316864983 -->


JavaScript has three types of declarations: var, let, and const. Variables declared with var are function scoped. Variables declared with let and const are block scoped. The difference between let and const is that the value of a variable declared with const cannot be changed -- it is read-only.

`const` prevents re-assignments, but it does not prevent changes to object properties. For example, the following code is perfectly valid:

```javascript
const person = {
  name: 'Lydia',
  age: 21
}
person.age = 22 // OK
```

The contents of an array are also not protected.

## Variable hoisting (var, let, const, and functions)

<!-- notecardId: 1705316864986 -->


var-declared variables are _hoisted_ to the top of their scope and initialized with a value of `undefined`. This means that a variable can be used before it has been declared.

Because of hoisting, all var statements in a function should be placed as near to the top of the function as possible. This best practice increases the clarity of the code.

By contrast, `let` and `const` are not hoisted. They are not initialized until their definition is evaluated. Accessing them before the initialization results in a `ReferenceError`.

Functions have a special status too with respect to hoisting. Unlike var declarations, which only hoist the declaration but not its value, function declarations are hoisted entirely — you can safely call the function anywhere in its scope. 


## when to use var, let, const

<!-- notecardId: 1705316864990 -->

When possible, use const for all references. If you must reassign references, use let instead of var, which isn't scoped to the block in which it's defined. **Basically, never use `var`.**

## null

<!-- notecardId: 1705316864993 -->


In JavaScript, a `null` value represents a reference that points deliberately to a nonexistent object or invalid memory. In code, it is represented as `null`. An impactful bug in JavaScript is that `typeof null` returns the string `'object'`. This is a bug because `null` is technically a JavaScript primitive. Still, for compatibility reasons, it will probably never be fixed.

## undefined

<!-- notecardId: 1705316864997 -->


`undefined` is a primitive value automatically assigned to variables that have just been declared but not initialized to a value. It is represented as `undefined` and has the type `undefined`. It is also the default return value of functions that do not return any other value, and the default value of function parameters that have not been passed any value when calling the function.

## Data type conversion

<!-- notecardId: 1705316865001 -->


Javascript automatically converts data types behind the scenes to perform certain operations. This is called _type coercion_. For example, the addition operator `+` does arithmetic addition when used on numbers, but it concatenates strings when used on strings. This means that if one of the operands of the addition operator is a string, the other operand is converted to a string. For example, `1 + '2'` evaluates to the string `'12'`. Similarly, the multiplication operator `*` does arithmetic multiplication when used on numbers, but it converts its operands to numbers when used on strings. For example, `'3' * '4'` evaluates to the number `12`.

## Converting strings to numbers

<!-- notecardId: 1705316865005 -->


A few options exist for converting strings to numbers in JavaScript. The most common is the unary plus operator `+`. For example, `+'42'` evaluates to the number `42`. Another option is the `Number()` function. For example, `Number('42')` also evaluates to the number `42`. A third option is the `parseInt()` function. For example, `parseInt('42')` also evaluates to the number `42`. The `parseInt()` function also takes a second parameter, the radix, which specifies the base of the number to be parsed. For example, `parseInt('11', 2)` evaluates to the number `3` because the string `'11'` is parsed as a binary number. `parseFloat()` is similar to `parseInt()` but it parses floating point numbers instead of integers.

## Array literals

<!-- notecardId: 1705316865008 -->


An array literal is a list of zero or more expressions, each of which represents an array element, enclosed in square brackets `[]`. When you create an array using an array literal, it is initialized with the specified values as its elements, and its length is set to the number of arguments specified.

## Extra commas in array literals

<!-- notecardId: 1705316865013 -->


If you put two commas in a row in an array literal, the array leaves an empty slot for the unspecified element. This empty entry is not explicitly undefined. It is just empty. This is not a problem if you use the array methods that ignore empty slots.

Still, it's generally better to explicitly specify undefined for each empty slot. This makes your code more readable and less error-prone.

## Block Statements

<!-- notecardId: 1705316865017 -->


The most basic statement is a block statement, which is used to group statements. The block is delimited by a pair of curly braces. They define a scope in which variables declared with let and const are accessible only within the block. Block statements are commonly used with control flow statements (e.g. if, for, while).

Use braces with all multiline blocks. If a block is just a single line, it is preferred not to use braces.

NOTE: var-declared variables are not block scoped. They are scoped to the function in which they are declared, or if declared outside of any function, to the global object. So their effects persist beyond the block itself.

## Using an assignment as a condition

<!-- notecardId: 1705316865020 -->


The assignment operator `=` returns the value of the variable after it has been assigned. This means that you can use any assignment as a condition. For example, the code `if (x = y)` assigns the value of `y` to `x` and then checks whether `x` is truthy. This is equivalent to `x = y; if (x)`. This is a common mistake. To avoid it, always use `===` instead of `=` inside conditionals. Sometimes, however, you might want to use an assignment as a condition on purpose. For example, the code `while ((line = readLine()) !== null)` reads lines from standard input in Node.js until the input ends. This tends to get flagged as an error by linters such as ESLint, and is easy to mistake for a typo, so it can be worth avoiding or explicitly signposting even when it's intentional.

## Falsy values

<!-- notecardId: 1705316865024 -->

Falsy values are values that are considered false when encountered in a Boolean context. There are 6 falsy values in JavaScript: `undefined`, `null`, `NaN`, `0`, `''` (empty string), and `false` (boolean false).

All other values -- including all objects -- evaluate to true when passed to a conditional statement.

## switch statement

<!-- notecardId: 1705316865029 -->

A switch statement allows a program to evaluate an expression and attempt to match the expression's value to a case label. If a match is found, the program executes the associated statement. A switch statement looks as follows:

```javascript
switch (expression) {
  case label_1:
    statements_1
    [break;]
  case label_2:
    statements_2
    [break;]
    ...
  default:
    statements_def
    [break;]
}
```

The optional `break` statement associated with each case label ensures that the program breaks out of switch once the matched statement is executed and continues execution at the statement following switch. If `break` is omitted, the program continues execution at the next statement in the switch statement.

## for statement

<!-- notecardId: 1705316865033 -->

A for loop repeats until a specified condition evaluates to false. Technically, for loops are not recommended in JavaScript. Instead, JavaScript's higher-order functions such as `map()` should be used instead. Use map() / every() / filter() / find() / findIndex() / reduce() / some() / ... to iterate over arrays, and Object.keys() / Object.values() / Object.entries() to produce arrays so you can iterate over objects.

A for statement looks as follows:

```javascript
for (initialization; condition; afterthought)
  statement
```

When a for loop executes, the following occurs:

1. The initializing expression `initialization`, if there is any, is executed. This expression usually initializes one or more loop counters, but the syntax allows an expression of any degree of complexity. This expression can also declare variables.
2. The condition expression is evaluated. If the value of condition is true, the loop statements execute. If the value of condition is false, the for loop terminates. If the condition expression is omitted entirely, the condition is assumed to be true.
3. The statement executes. To execute multiple statements, use a block statement (`{ ... }`) to group those statements.
4. If present, the update expression `afterthought` is executed.

Apparently, each of the three expressions can be omitted. For example, the following is an infinite loop that prints "hi" forever and never terminates:

```javascript
for (;;) {
  console.log("hi");
}
```

## Higher Order Functions

<!-- notecardId: 1705316865037 -->

It's recommended not to use iterators. Prefer JavaScript's higher-order functions instead of loops like for-in or for-of.

Why? This enforces our immutable rule. Dealing with pure functions that return values is easier to reason about than side effects.

Use map() / every() / filter() / find() / findIndex() / reduce() / some() / ... to iterate over arrays, and Object.keys() / Object.values() / Object.entries() to produce arrays so you can iterate over objects.

```javascript
const numbers = [1, 2, 3, 4, 5];

// bad
let sum = 0;
for (let num of numbers) {
  sum += num;
}
sum === 15;

// good
let sum = 0;
numbers.forEach((num) => {
  sum += num;
});
sum === 15;

// best (use the functional force)
const sum = numbers.reduce((total, num) => total + num, 0);
sum === 15;

// bad
const increasedByOne = [];
for (let i = 0; i < numbers.length; i++) {
  increasedByOne.push(numbers[i] + 1);
}

// good
const increasedByOne = [];
numbers.forEach((num) => {
  increasedByOne.push(num + 1);
});

// best (keeping it functional)
const increasedByOne = numbers.map((num) => num + 1);
```

## do...while statement

<!-- notecardId: 1705316865041 -->

The do...while statement repeats until a specified condition evaluates to false. A do...while statement looks as follows:

```javascript
do
  statement
while (condition);
```

The statement is always executed once before the condition is checked. To execute multiple statements within the loop, use a block statement (`{ ... }`) to group those statements.

## labeled statement

<!-- notecardId: 1705316865045 -->

A labeled statement is any statement that is prefixed with an identifier. You can jump to this label using a break or continue statement nested within the labeled statement.

```javascript
// The first for statement is labeled "loop1"
loop1: for (let i = 0; i < 3; i++) {
  // The second for statement is labeled "loop2"
  loop2: for (let j = 0; j < 3; j++) {
    if (i === 1 && j === 1) {
      continue loop1;
    }
    console.log(`i = ${i}, j = ${j}`);
  }
}
```

## continue statement

<!-- notecardId: 1705316865050 -->

The continue statement can be used to restart a while, do-while, for, or label statement.

## break statement

<!-- notecardId: 1705316865054 -->

Use the break statement to terminate a loop, switch, or in conjunction with a labeled statement.

## for...in statement

<!-- notecardId: 1705316865058 -->

The for...in statement iterates over all enumerable properties of an object that are keyed by strings (ignoring ones keyed by Symbols), including inherited enumerable properties.

```javascript
for (variable in object) {
  statements
}
```

## Using arrays with for...in 

<!-- notecardId: 1705316865062 -->

Array indexes are just enumerable properties with integer names and are otherwise identical to general Object properties. There is no guarantee that for...in will return the indexes in any particular order. The for...in loop statement will return all enumerable properties, including those with non–integer names and those that are inherited.  

Therefore, it is better to use a traditional for loop with a numeric index when iterating over arrays, because the for...in statement iterates over user-defined properties in addition to the array elements, if you modify the Array object, such as adding custom properties or methods.

## for...of statement

<!-- notecardId: 1705316865067 -->

The for...of statement creates a loop iterating over iterable objects (including Array, Map, Set, arguments object and so on), invoking a custom iteration hook with statements to be executed for the value of each distinct property.

```javascript
for (variable of iterable) {
  statement
}
```

## for...of vs for...in

<!-- notecardId: 1705316865071 -->

While for...in iterates over property names, for...of iterates over property values:

```javascript
const arr = [3, 5, 7];
arr.foo = "hello";

for (const i in arr) {
  console.log(i);
}
// "0" "1" "2" "foo"

for (const i of arr) {
  console.log(i);
}
// Logs: 3 5 7
```

## What happens when you pass a parameter to a function?

<!-- notecardId: 1705316865075 -->

When you pass a value as a parameter, the function creates a local copy of the value. So, if you change the parameter inside the function, it has no effect on the argument.

When you pass an object as a parameter, if the function changes the object's properties, that change is visible outside the function.

When you pass an array as a parameter, if the function changes any of the array's values, that change is visible outside the function.

## Function expressions

<!-- notecardId: 1705316865079 -->

The function keyword can be used to define a function inside an expression. In general, prefer to use named function expressions instead of function declarations.

The main difference between a function expression and a function declaration is the function name, which can be omitted in function expressions to create anonymous functions. A function expression can be used as an IIFE (Immediately Invoked Function Expression) which runs as soon as it is defined. 

Function expressions in JavaScript are not hoisted, unlike function declarations. You can't use function expressions before you create them. This makes them preferable in most cases.

If you want to refer to the current function inside the function body, you need to create a named function expression. This name is then local only to the function body (scope). In general, named function expressions are preferable to anonymous function expressions since they provide additional debugging information.

Function expressions are convenient when passing a function as an argument to another function. 

## Immediately Invoked Function Expressions (IIFE)

<!-- notecardId: 1705316865083 -->

An IIFE (Immediately Invoked Function Expression) is a JavaScript function that runs as soon as it is defined. IIFEs are very useful because they don't pollute the global object, and they are a simple way to isolate variables declarations. 

Wrap immediately invoked function expressions in parentheses. An immediately invoked function expression is a single unit - wrapping both it, and its invocation parens, in parens, cleanly expresses this. Note that in a world with modules everywhere, you almost never need an IIFE.

```javascript
// immediately-invoked function expression (IIFE)
(function () {
  console.log('Welcome to the Internet. Please follow me.');
}());
```

## The arguments object

<!-- notecardId: 1705316865088 -->

The arguments of a function are maintained in an array-like object. Within a function, you can address the arguments passed to it as follows:

```javascript
arguments[i]
```

where `i` is the ordinal number of the argument, starting at zero. So, the first argument passed to a function would be `arguments[0]`. The total number of arguments is indicated by `arguments.length`.

Using the arguments object, you can call a function with more arguments than it is formally declared to accept.

For example, consider a function that concatenates several strings. The only formal argument for the function is a string that specifies the characters that separate the items to concatenate. The function is defined as follows:

```javascript
function myConcat(separator) {
  var result = ''; // initialize list
  var i;
  // iterate through arguments
  for (i = 1; i < arguments.length; i++) {
    result += arguments[i] + separator;
  }
  return result;
}
```

Never name a parameter arguments. This will take precedence over the arguments object that is given to every function scope.

## default parameters

<!-- notecardId: 1705316865092 -->

In JavaScript, parameters of functions default to undefined. However, in some situations it might be useful to set a different default value. 

With default parameters, a manual check in the function body is no longer necessary. You can put 1 as the default value for b in the function head:

```javascript
function multiply(a, b = 1) {
  return a * b;
}

console.log(multiply(5)); // 5
```

## Rest parameters

<!-- notecardId: 1705316865096 -->

The rest parameter syntax allows us to represent an indefinite number of arguments as an array. With rest parameters, you can create functions that take a variable number of arguments. These arguments are stored in an array that can be accessed later from inside the function.

```javascript
function multiply(multiplier, ...theArgs) {
  return theArgs.map(x => multiplier * x);
}
```

Never use arguments, opt to use rest syntax `...` instead. `...` is explicit about which arguments you want pulled. Plus, rest arguments are a real Array, and not merely Array-like like arguments.

## Arrow functions

<!-- notecardId: 1705316865100 -->

An arrow function expression is a compact alternative to a traditional function expression, but is limited and can't be used in all situations. When you must use an anonymous function (as when passing an inline callback), use arrow function notation. 

```javascript

// Traditional Function Expression
function (a) {
  return a + 100;
}

// Arrow Function Expression
(a) => a + 100;

// Traditional Function Expression
function (a, b) {
  return a + b + 100;
}

// Arrow Function Expression
(a, b) => a + b + 100;

```

Always include parentheses around arguments for clarity and consistency. 

## Equal vs Strict Equal

<!-- notecardId: 1705316865104 -->

The identity (`===`) operator behaves identically to the equality (`==`) operator except no type conversion is done, and the types must be the same to be considered equal.

## Decrement and Increment

<!-- notecardId: 1705316865109 -->

The decrement operator (`--`) decrements (subtracts one from) its operand and returns a value. Avoid using unary increments and decrements (++, --). 

If used postfix, with operator after operand (for example, `x--`), then it returns the value before decrementing.

If used prefix, with operator before operand (for example, `--x`), then it returns the value after decrementing.

Example: If x is 3, then --x sets x to 2 and returns 2, whereas x-- returns 3 and, only then, sets x to 2.

Increment (`++`) increments (adds one to) its operand and returns a value.

## Destructuring assignment

<!-- notecardId: 1705316865113 -->

The destructuring assignment syntax is a JavaScript expression that makes it possible to unpack values from arrays, or properties from objects, into distinct variables. Destructuring saves you from creating temporary references for those properties, and from repetitive access of the object. Use object destructuring when accessing and using multiple properties of an object. 

```javascript
var a, b, rest;
[a, b] = [10, 20];
console.log(a);
// expected output: 10

console.log(b);
// expected output: 20

[a, b, ...rest] = [10, 20, 30, 40, 50];
console.log(rest);
// expected output: Array [30,40,50]
```

## Object destructuring vs Array destructuring

<!-- notecardId: 1705316865116 -->

Array destructuring is similar to object destructuring. The main difference is that you can use any name for variables when using object destructuring, but with array destructuring the name of the variables must be the same as the array's keys.

Use object destructuring for multiple return values, not array destructuring. Why? You can add new properties over time or change the order of things without breaking call sites.

```javascript
// bad
function processInput(input) {
  // then a miracle occurs
  return [left, right, top, bottom];
}

// the caller needs to think about the order of return data
const [left, __, top] = processInput(input);

// good
function processInput(input) {
  // then a miracle occurs
  return { left, right, top, bottom };
}

// the caller selects only the data they need
const { left, top } = processInput(input);
```

## Conditional (ternary) operator

<!-- notecardId: 1705316865120 -->

The conditional operator is the only JavaScript operator that takes three operands: a condition followed by a question mark (`?`), then an expression to execute if the condition is truthy followed by a colon (`:`), and finally the expression to execute if the condition is falsy. This operator is frequently used as a shortcut for the if statement.

```javascript
var age = 26;
var beverage = (age >= 21) ? "Beer" : "Juice";
console.log(beverage); // "Beer"
```

## Spread syntax

<!-- notecardId: 1705316865125 -->

The spread (...) syntax allows an iterable, such as an array or string, to be expanded in places where zero or more arguments (for function calls) or elements (for array literals) are expected. 

Spread syntax looks exactly like rest syntax. In a way, spread syntax is the opposite of rest syntax. Spread syntax "expands" an array into its elements, while rest syntax collects multiple elements and "condenses" them into a single element. 

Prefer the use of the spread syntax ... to call variadic functions. 

```javascript
// bad
const x = [1, 2, 3, 4, 5];
console.log.apply(console, x);

// good
const x = [1, 2, 3, 4, 5];
console.log(...x);

// bad
new (Function.prototype.bind.apply(Date, [null, 2016, 8, 5]));

// good
new Date(...[2016, 8, 5]);
```

## Comma operator

<!-- notecardId: 1705316865129 -->

The comma operator (``,) evaluates each of its operands (from left to right) and returns the value of the last operand. This lets you create a compound expression in which multiple expressions are evaluated, with the compound expression's final value being the value of the rightmost of its member expressions. This is commonly used to provide multiple parameters to a for loop.

```javascript

const x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const a = [x, x, x, x, x];

for (let i = 0, j = 9; i <= j; i++, j--) {
  //                              ^
  console.log(`a[${i}][${j}]= ${a[i][j]}`);
}
```

## Creating Arrays

<!-- notecardId: 1705316865133 -->

There are a few ways to create an array. The recommended way is to use the literal syntax:

```javascript
// bad
const items = new Array();

// good
const items = [];
```

## Adding items to an array

<!-- notecardId: 1705316865136 -->

There are a few ways to add items to an array. The recommended way is to use the `push` method:

```javascript
const someStack = [];

// bad
someStack[someStack.length] = 'abracadabra';

// good
someStack.push('abracadabra');
```

## Copying an array

<!-- notecardId: 1705316865140 -->

There are a few ways to copy arrays. Recommended practice is to use array spreads `...`.

```
// bad
const len = items.length;
const itemsCopy = [];
let i;

for (i = 0; i < len; i += 1) {
  itemsCopy[i] = items[i];
}

// good
const itemsCopy = [...items];
```

## Converting an iterable to an array

<!-- notecardId: 1705316865145 -->

Use spreads `...` to convert an iterable object to an array.

```javascript
const foo = document.querySelectorAll('.foo');

// good
const nodes = Array.from(foo);

// best
const nodes = [...foo];
```

## Converting an array-like object to an array

<!-- notecardId: 1705316865149 -->

Use `Array.from` to convert an array-like object to an array.

```javascript
const arrLike = { 0: 'foo', 1: 'bar', 2: 'baz', length: 3 };

// bad
const arr = Array.prototype.slice.call(arrLike);

// good
const arr = Array.from(arrLike);
```

## Mapping over iterables

<!-- notecardId: 1705316865154 -->

Use Array.from instead of spread ... for mapping over iterables, because it avoids creating an intermediate array.

```javascript
// bad
const baz = [...foo].map(bar);

// good
const baz = Array.from(foo, bar);
```

## Line breaks in multi-line array literals

<!-- notecardId: 1705316865160 -->

Use line breaks after opening array brackets and before closing array brackets, if an array has multiple lines.

```javascript
// bad
const arr = [
  [0, 1], [2, 3], [4, 5],
];

const objectInArray = [{
  id: 1,
}, {
  id: 2,
}];

const numberInArray = [
  1, 2,
];

// good
const arr = [[0, 1], [2, 3], [4, 5]];

const objectInArray = [
  {
    id: 1,
  },
  {
    id: 2,
  },
];

const numberInArray = [
  1,
  2,
];
```

## Defining strings

<!-- notecardId: 1705316865164 -->

Style guides recommend using single quotes '' for strings. 

```javascript
// bad
const name = "Capt. Janeway";

// bad - template literals should contain interpolation or newlines
const name = `Capt. Janeway`;

// good
const name = 'Capt. Janeway';
```

## Long Strings

<!-- notecardId: 1705316865169 -->

Strings that cause the line to go over 100 characters should not be written across multiple lines using string concatenation. Why? Broken strings are painful to work with and make code less searchable.

```javascript
// bad
const errorMessage = 'This is a super long error that was thrown because \
of Batman. When you stop to think about how Batman had anything to do \
with this, you would get nowhere \
fast.';

// bad
const errorMessage = 'This is a super long error that was thrown because ' +
  'of Batman. When you stop to think about how Batman had anything to do ' +
  'with this, you would get nowhere fast.';

// good
const errorMessage = 'This is a super long error that was thrown because of Batman. When you stop to think about how Batman had anything to do with this, you would get nowhere fast.';
```

## Template Literals

<!-- notecardId: 1705316865173 -->

When programmatically building up strings, use template strings instead of concatenation. Template strings give you a readable, concise syntax with proper newlines and string interpolation features.

```javascript
// bad
function sayHi(name) {
  return 'How are you, ' + name + '?';
}

// bad
function sayHi(name) {
  return ['How are you, ', name, '?'].join();
}

// bad
function sayHi(name) {
  return `How are you, ${ name }?`;
}

// good
function sayHi(name) {
  return `How are you, ${name}?`;
}
```

## Accessing Properties

<!-- notecardId: 1705316865179 -->

There are two ways to access properties: dot notation and bracket notation. Dot notation is preferred.

```javascript
const luke = {
  jedi: true,
  age: 28,
};

// bad
const isJedi = luke['jedi'];

// good
const isJedi = luke.jedi;
```

But use bracket notation when accessing properties with a variable.

```javascript
const luke = {
  jedi: true,
  age: 28,
};

function getProp(prop) {
  return luke[prop];
}

const isJedi = getProp('jedi');
```

## Where to assign variables

<!-- notecardId: 1705316865183 -->

Assign variables where you need them, but place them in a reasonable place.

Also, group all your consts and then group all your lets.

## TODO and FIXME

<!-- notecardId: 1705316865187 -->

Use `// TODO:` to annotate solutions that are temporary, a short-term solution, or good-enough but not perfect. Use `// FIXME:` to annotate problems.

 Prefixing your comments with FIXME or TODO helps other developers quickly understand if you’re pointing out a problem that needs to be revisited, or if you’re suggesting a solution to the problem that needs to be implemented. These are different than regular comments because they are actionable. 

## Whitespace

<!-- notecardId: 1705316865191 -->

Use soft tabs set to 2 spaces. 

Place 1 space before the leading brace.

Place 1 space before the opening parethesis of a control statement. Place no space between the argument list and the function name in function calls and declarations. 

Set off operators with spaces. 

End files with a single newline character.

Use indentation when making long method chains (more than 2 method chains). Use a leading dot, which emphasizes that the line is a method call, not a new statement. 

Leave a blank line after blocks and before the next statement.

Do not pad your blocks with blank lines.

Add spaces inside curly braces.

Avoid spaces before commas and require a space after commas. 

Trailing commas are good, make for cleaner git diffs.

## Semicolons

<!-- notecardId: 1705316865195 -->

Use semicolons at the end of each statement.

## Naming Conventions

<!-- notecardId: 1705316865199 -->

Use camelCase when naming objects, functions, and instances.

Avoid single letter names. Be descriptive with your naming.

Use PascalCase when naming constructors or classes.

Do not use trailing or leading underscores; JavaScript does not have privacy.

Acronyms and initialisms should always be all uppercased, or all lowercased.

