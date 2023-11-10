const sharp = require("sharp");
const AWS = require("aws-sdk");

exports.handler = async function (event, context) {
  const { BUCKET_IMAGES } = process.env;
  const { id } = event;
  if (!id) {
    throw new Error("Invalid id");
  }

  const getTiff = await fetch(
    `https://resultados.gob.ar/backend-difu/scope/data/getTiff/${id}`
  );
  const { encodingBinary } = await getTiff.json();
  const buffer = Buffer.from(encodingBinary, "base64");
  const firstPage = await sharp(buffer, { page: 0 }).toBuffer();

  const path = `actas/${id}.jpeg`;
  const opts = {
    Bucket: BUCKET_IMAGES,
    Key: path,
    ContentEncoding: "base64",
    Body: firstPage,
    ACL: "public-read",
  };
  const bucket = new AWS.S3();
  await bucket.putObject(opts).promise();

  return path;
};
