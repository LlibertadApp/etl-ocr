exports.handler = async function (event, context) {
  const { GetResultsFromApi } = event;
  if (!GetResultsFromApi) {
    throw Error("Invalid GetResultsFromApi");
  }

  const { partidos, recurridos, blancos, impugnados, nulos, totalVotos } =
    GetResultsFromApi;

  // sumatoria de votos de todos los partidos disponibles
  const totalPartidos = partidos.reduce(
    (accu, current) => accu + current.votos,
    0
  );

  return {
    sum: recurridos + blancos + impugnados + nulos + totalPartidos,
    total: totalVotos,
  };
};
