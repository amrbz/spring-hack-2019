
import Index from './Index';
import Utils from './Utils';
import Qr from './Qr';

const stores = {};

stores.index = new Index(stores);
stores.utils = new Utils(stores);
stores.qr = new Qr(stores);

export default stores;
