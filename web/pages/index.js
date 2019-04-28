import React from 'react';
import PropTypes from 'prop-types';
import Router, { withRouter } from 'next/router';
import { observer, inject } from 'mobx-react';
import { autorun } from 'mobx';
import { Row, Col, Drawer, Button, Modal, Divider } from 'antd';

@inject('index')
@observer
class Index extends React.Component {

    constructor(props) {
        super(props);

        const { index } = props;

        this.listPeriodicChecker = autorun(() => {
            if (index.getListStatus === 'success') {
                index.getRequests();
            }
        })
    }

    componentDidMount() {
        const { index } = this.props;
        index.getRequests();
    }

    componentWillUnmount() {
        this.listPeriodicChecker();
    }
    
    render() {
        const { index, major } = this.props;
        return (
            <div>
                <Row>
                    <Col xs={{ span: 14, offset: 5}}>
                        <h1>Requests</h1>
                    </Col>
                </Row>
                <Row>
                    <Col xs={{ span: 14, offset: 5}}>
                        <div className="requests">
                            {index.list.length === 0 && <div>No requests so far</div>}
                            {index.list.map((item, el) => (
                                <div key={`key_${item.id}`}>
                                    <h3><span>#{el + 1}</span></h3>
                                    <p><span className="th">Passport:</span>{item.passport}</p>
                                    <p><span className="th">Public Key:</span>{item.publicKey}</p>
                                    {item.verified === false ? (
                                        <Button
                                            type="primary"
                                            onClick={() => {
                                                index.sendConfirm(item);
                                            }}
                                            loading={index.sendConfirmStatus === 'fetching' && index.itemToConfirm &&   index.itemToConfirm.id === item.id}
                                        >
                                            Confirm
                                        </Button>
                                    ) : (
                                        <p><span className="th">Ciphertext:</span>{item.cypherText || '--'}</p>
                                    )}
                                    <Divider />
                                </div>
                            ))}
                        </div>
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

Index.propTypes = {
    index: PropTypes.object,
};

export default withRouter(Index)