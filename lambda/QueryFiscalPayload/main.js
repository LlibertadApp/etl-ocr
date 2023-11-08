exports.handler = async function (event, context) {
  const { id } = event;
  if (!id) {
    throw new Error("Invalid id");
  }

  let fiscalData = {
    isAvailable: false,
  };

  // query a dynamodb (dax) usando el id de la mesa
  fiscalData = Object.assign(fiscalData, {
    mesaId: "",
    conteoLla: 0,
    conteoUp: 0,
    votosImpugnados: 0,
    votosNulos: 0,
    votosEnBlanco: 0,
    votosRecurridos: 0,
    votosEnTotal: 0,
    userId: "",
    imagePath: "",
  });

  return fiscalData;
};
