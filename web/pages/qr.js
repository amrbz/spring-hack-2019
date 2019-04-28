import React from 'react';
import PropTypes from 'prop-types';
import Router, { withRouter } from 'next/router';
import { observer, inject } from 'mobx-react';
import { autorun } from 'mobx';
import { Row, Col, Drawer, Button, Modal, Divider } from 'antd';

@inject('qr')
@observer
class Qr extends React.Component {

    constructor(props) {
        super(props);

        const { qr } = props;
        this.listPeriodicChecker = autorun(() => {
            if (qr.getListStatus === 'success') {
                qr.getList();
            }
        })
    }

    componentDidMount() {
        const { qr } = this.props;
        qr.getList();
    }

    componentWillUnmount() {
        this.listPeriodicChecker();
    }

    render() {
        const { qr } = this.props;
        return (
            <div>
                <Row>
                    <Col xs={{ span: 14, offset: 5}}>
                        <h1>QR codes</h1>
                    </Col>
                </Row>
                <Row>
                    <Col xs={{ span: 14, offset: 5}}>
                        {qr.list.length === 0 && <div>No requests so far</div>}
                        {qr.list.map((item, el) => (
                            <div key={`key_${item.id}`}>
                                <h3><span>#{el + 1}</span></h3>
                                <p><span className="th">Passport:</span>{item.passport}</p>
                                <p><span className="th">Secret:</span>{item.secret}</p>
                                {item.verified === false ? (
                                    <Button
                                        type="primary"
                                        onClick={() => {
                                            qr.sendConfirm(item);
                                        }}
                                        loading={qr.sendConfirmStatus === 'fetching' && qr.itemToConfirm &&   qr.itemToConfirm.id === item.id}
                                    >
                                        Confirm
                                    </Button>
                                ) : (
                                    <p><img src={item.qrCode} className="qrCode" /></p>
                                )}
                                <Divider />
                            </div>
                        ))}
                    </Col>
                </Row>
                <style jsx>{`
                    h1 {
                        margin-top: 4em;
                        margin-bottom: 2em;
                        font-family: 'Roboto', sans-serif;
                        font-weight: 100;
                    }

                    h3 span {
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        text-align: center;
                        line-height: 40px;
                        border-radius: 50%;
                        background: #000;
                        color: #fff;
                        margin-bottom: 1em;
                    }

                    span.th {
                        display: inline-block;
                        min-width: 100px;
                        font-weight: bold;
                    }

                    .requests {
                        padding-bottom: 4em;
                    }

                    .qrCode {
                        border: 1px solid #ddd;
                    }

                    p {
                        display: -webkit-box;
                        -webkit-line-clamp: 1;
                        -webkit-box-orient: vertical;
                        width: 100%;
                        text-overflow: ellipsis;
                        overflow-y: hidden;
                        word-break: break-all;
                    }
                `}</style>
            </div>
        );
    }
}

Qr.propTypes = {
    qr: PropTypes.object,
};

export default withRouter(Qr)