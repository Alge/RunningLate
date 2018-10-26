import * as sapper from '../__sapper__/client.js';
import { Store } from 'svelte/store.js';

class GeoStore extends Store {
  constructor(data) {
    super(data);

    this.id = null;
  }

  start() {
    if (this.id !== null) return;

    this.id = navigator.geolocation.watchPosition((position) => {
      this.set({position});
    }, console.error, {enableHighAccuracy: true});

    return this;
  }

  stop() {
    navigator.geolocation.clearWatch(this.id);
    this.id = null;
    return this;
  }
}

sapper.start({
	target: document.querySelector('#sapper'),
  store: data => new GeoStore(data).start(),
});
