import React from 'react';
import PropTypes from 'prop-types';
import DataTable, { createTheme } from 'react-data-table-component';
import NoAssetsFound from './NoAssetsFound';

export default class CollectionListView extends React.Component {
    render() {
        if (this.props.assetList.length === 0) {
            return <NoAssetsFound />;
        } else {
            const columns = [
                {
                    name: 'Title',
                    selector: 'title',
                    sortable: true
                },
                {
                    name: 'Tags',
                    selector: 'tags',
                    sortable: true
                },
                {
                    name: 'Terms',
                    selector: 'terms',
                    sortable: true
                },
                {
                    name: 'Media',
                    selector: 'primary_type',
                    sortable: true
                },
                {
                    name: 'Owner',
                    selector: 'author.public_name',
                    sortable: true
                },
                {
                    name: 'Date',
                    selector: 'modified',
                    sortable: true
                }
            ];

            createTheme('mediathread', {
                striped: {
                    default: 'rgba(0, 0, 0, 0.05)'
                }
            });

            const styles = {
                header: {
                    style: {
                        minHeight: 0
                    }
                },
                headRow: {
                    style: {
                        minHeight: '34px'
                    }
                },
                headCells: {
                    style: {
                        color: 'rgba(33, 37, 41)',
                        fontSize: '16px',
                        fontWeight: 700,
                        backgroundColor: '#ccc',
                        borderColor: '#ccc',
                        padding: '0.3rem'
                    }
                },
                rows: {
                    style: {
                        fontSize: '16px'
                    }
                },
                cells: {
                    style: {
                        padding: '0.3rem'
                    }
                }
            };

            return (
                <DataTable
                    theme="mediathread"
                    customStyles={styles}
                    columns={columns}
                    highlightOnHover={true}
                    striped={true}
                    data={this.props.assetList} />
            );
        }
    }
}

CollectionListView.propTypes = {
    assetList: PropTypes.array
};
