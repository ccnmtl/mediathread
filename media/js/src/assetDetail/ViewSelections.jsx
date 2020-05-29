/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

import Asset from '../Asset';
import SelectionAccordionItem from '../SelectionAccordionItem';

export default class ViewSelections extends React.Component {
    constructor(props) {
        super(props);
        this.asset = new Asset(this.props.asset);
    }

    render() {
        const type = this.asset.getType();

        const selectionsByAuthor = {};
        const selectionsByAuthorDom = [];

        const me = this;

        // Group the selections by author.
        this.props.asset.annotations.forEach(function(s) {
            if (selectionsByAuthor[s.author.id]) {
                selectionsByAuthor[s.author.id].push(s);
            } else {
                selectionsByAuthor[s.author.id] = [s];
            }
        });

        for (let [key, selections] of Object.entries(selectionsByAuthor)) {
            let selectionsDom = [];
            selections.forEach(function(s) {
                selectionsDom.push(
                    <SelectionAccordionItem
                        key={s.id}
                        asset={me.props.asset}
                        type={type}
                        selection={s}
                        onClickPlay={me.props.onClickPlay}
                        onClickSelection={me.props.onClickSelection}
                        showDeleteDialog={me.props.showDeleteDialog}
                    />
                );
            });

            let authorName = selections[0].author.public_name ||
                selections[0].author.username;

            let authorAccordion = (
                <div key={key} className="accordion" id="accordionExample2">
                    <div className="card">
                        <div className="card-header" id="headingOne">
                            <h2 className="mb-0">
                                <button
                                    className="btn btn-link" type="button"
                                    data-toggle="collapse" data-target="#collapseOne"
                                    aria-expanded="true" aria-controls="collapseOne">
                                    {authorName}
                                </button>
                            </h2>
                        </div>
                        <div
                            id="collapseOne"
                            className="collapse hide"
                            aria-labelledby="headingOne"
                            data-parent="#accordionExample2">
                            {selectionsDom}
                        </div>
                    </div>
                </div>
            );

            selectionsByAuthorDom.push(authorAccordion);
        }

        return (
            <React.Fragment>
                <h2>Selections from &quot;{this.props.asset.title}&quot;</h2>
                <div
                    className="accordion" id="selectionAccordion"
                    style={{margin: '1em 0em 1em 0em'}}>
                </div>

                {selectionsByAuthorDom}

                <Modal
                    show={this.props.showDeleteDialogBool}
                    onHide={this.props.hideDeleteDialog}>
                    <Modal.Header closeButton>
                        <Modal.Title>Delete annotation</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>Delete this annotation?</Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={this.hideDeleteDialog}>
                            Cancel
                        </Button>
                        <Button variant="danger" onClick={this.onDeleteSelection}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
            </React.Fragment>
        );

    }
}

ViewSelections.propTypes = {
    asset: PropTypes.object,
    onClickPlay: PropTypes.func.isRequired,
    onClickSelection: PropTypes.func.isRequired,
    hideDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialogBool: PropTypes.bool.isRequired
};
