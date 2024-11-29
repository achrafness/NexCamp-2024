const express = require("express");
const app = express();
const port = 3000;

let cars = [
  { id: 1, make: "Toyota", model: "Corolla", year: 2020 },
  { id: 2, make: "Honda", model: "Civic", year: 2021 },
];

// READ: Get all cars
app.get("/cars", (req, res) => {
  res.status(200).json(cars);
});

app.get("/cars/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const car = cars.find((car) => car.id === id);
  if (!car) {
    res.status(404).json({ error: "Car not found" });
  } else {
    res.status(200).json(car);
  }
});
app.post("/cars", (req, res) => {
  const car = req.body;
  cars.push(car);
  res.status(201).json(car);
});
app.get("/Ahmed", (req, res) => {
  res.status(200).json({ flag: "n3xus{Ahm3d_was_h3r3}" });
});
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});