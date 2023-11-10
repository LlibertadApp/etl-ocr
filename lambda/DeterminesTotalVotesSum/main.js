exports.handler = async function (event, context) {
  const { govermentData } = event;
  if (!govermentData) {
    throw Error("Invalid govermentData");
  }

  const {
    resultados,
    id,
    recurridos,
    blancos,
    impugnados,
    nulos,
    electores,
    sobres,
    totalVotos,
  } = govermentData;

  // sumatoria de votos de todos los partidos disponibles
  const totalPartidos = resultados.reduce(
    (accu, current) => accu + current.votos,
    0
  );

  return {
    sum: recurridos + blancos + impugnados + nulos + totalPartidos,
    total: totalVotos,
  };
};
