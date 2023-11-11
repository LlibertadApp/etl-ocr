exports.handler = async function (event, context) {
  const { GetResultsFromApi } = event;
  if (!GetResultsFromApi) {
    throw Error("Invalid GetResultsFromApi");
  }

  const {
    partidos,
    id,
    recurridos,
    blancos,
    impugnados,
    nulos,
    electores,
    sobres,
    totalVotos,
  } = GetResultsFromApi;

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
