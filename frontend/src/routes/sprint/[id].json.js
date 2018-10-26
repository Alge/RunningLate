import fetch from 'node-fetch';
import FormData from 'form-data';

export async function get(req, res, next) {
  const { id } = req.params;

  try {
    const response = await fetch(process.env.BACKEND + '/sprint/' + id);
    const data = await response.json();

    console.log(data);

    res.writeHead(200, {
      'Content-Type': 'application/json'
    });

    res.end(JSON.stringify(data));
  } catch (e) {
    res.writeHead(500, {
      'Content-Type': 'application/json'
    });

    res.end(JSON.stringify({
      message: String(e)
    }));
  }
}
