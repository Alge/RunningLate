import fetch from 'node-fetch';
import FormData from 'form-data';

export async function get(req, res, next) {
  // the `slug` parameter is available because
  // this file is called [slug].json.js
  const { coords } = req.params;

  let params;
  try {
    params = coords.split(',');
    if (params.length != 4) throw new Error(`Expected 4 coords`);
  } catch (e) {
    res.writeHead(404, {
      'Content-Type': 'application/json',
    });
    res.end(JSON.stringify({
      message: `Bad format: ${String(e)}`,
    }));
    return;
  }

  try {
    const form = new FormData();
    ['startLat', 'startLong', 'endLat', 'endLong'].forEach((name, i) => {
      form.append(name, params[i]);
    });
    const response = await fetch(process.env.BACKEND + '/get_route', {
      method: 'POST',
      body: form,
    });
    const data = await response.json();
    delete data.decon_id;

    res.writeHead(200, {
      'Content-Type': 'application/json'
    });
    res.end(JSON.stringify(data));
  } catch (e) {
    res.writeHead(500, {
      'Content-Type': 'application/json',
    });
    res.end(JSON.stringify({
      message: String(e),
    }));
  }
}
