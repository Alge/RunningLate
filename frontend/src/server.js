import sirv from 'sirv';
import polka from 'polka';
import compression from 'compression';
import * as sapper from '../__sapper__/server.js';
import { Store } from 'svelte/store.js';

const { PORT, NODE_ENV } = process.env;
const dev = NODE_ENV === 'development';

polka() // You can also use Express
	.use(
		compression({ threshold: 0 }),
		sirv('static', { dev }),
		sapper.middleware({
      store: request => new Store({
        position: {
          coords: {
            accuracy: 1000,
            latitude: 59.3826,
            longitude: 18.0285, // 18
          },
        },
        backend: process.env.BACKEND,
      }),
    })
	)
	.listen(PORT, err => {
		if (err) console.log('error', err);
	});
