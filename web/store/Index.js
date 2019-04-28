import { action, observable } from 'mobx';
import axios from 'axios';

class AliceStore {
    stores = null;
    constructor(stores) {
        this.stores = stores;
    }

    @observable list = [];
    @observable getListStatus = 'init';
    @observable sendConfirmStatus = 'init';
    @observable itemToConfirm = null;

    @action
    getRequests() {
        this.itemToConfirm = null;
        const { utils } = this.stores;
        utils.sleep(this.getListStatus === 'init' ? 0: 500).then(_ => {
            this.getListStatus = 'fetching';
            axios
                .get(`${process.env.API_HOST}/api/v1/sber`)
                .then(res => {
                    this.list = res.data;
                    this.getListStatus = 'success';
                })
                .catch(e => {
                    this.getListStatus = 'error';
                    console.log(e);
                });
        })
    }

    @action
    sendConfirm(item) {
        this.itemToConfirm = item;
        const formConfig = {};
        const formData = new FormData();
        // formData.append('id', item.id);
        formData.append('publicKey', item.publicKey);

        this.sendConfirmStatus = 'fetching';
        axios
            .put(`${process.env.API_HOST}/api/v1/sber`, formData, formConfig)
            .then(res => {
                // this.sendConfirmStatus = 'success';
            })
            .catch(e => {
                // this.sendConfirmStatus = 'error';
                console.log(e);
            })
    }
}

export default AliceStore;

