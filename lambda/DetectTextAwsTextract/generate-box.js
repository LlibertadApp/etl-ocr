// generate coords from
// https://hermitter.github.io/Polygon-Coordinates/

const box = () => {
  // medidas del telegrama
  const WIDTH = 300;
  const HEIGHT = 544;

  const points = [
    { x: 4, y: 4 },
    { x: 298, y: 4 },
    { x: 298, y: 78 },
    { x: 4, y: 78 },
  ];

  const coordinates = [];
  for (const coord of points) {
    const x = parseFloat((coord.x / WIDTH).toFixed(5));
    const y = parseFloat((coord.y / HEIGHT).toFixed(5));
    coordinates.push([x, y]);
  }

  console.log(JSON.stringify(coordinates));
};
box();
