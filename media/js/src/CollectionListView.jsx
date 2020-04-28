import React from 'react';
import PropTypes from 'prop-types';
import DataTable, { createTheme } from 'react-data-table-component';
import LoadingAssets from './alerts/LoadingAssets';
import NoAssetsFound from './alerts/NoAssetsFound';
import {formatDay, getAssets} from './utils';

export default class CollectionListView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false
        };

        this.handleSort = this.handleSort.bind(this);
    }
    handleSort(column, sortDirection) {
        this.setState({loading: true});

        let sortField = column.name.toLowerCase();
        if (sortField === 'owner') {
            sortField = 'author';
        } else if (sortField === 'date') {
            sortField = 'modified';
        }

        const orderBy = sortDirection === 'asc' ? sortField : '-' + sortField;

        const me = this;
        getAssets(
            // TODO: pass in correct filters here
            '', '', [], [], 'all',
            0, orderBy
        ).then(function(d) {
            me.props.onUpdateAssets(d.assets, d.asset_count);
            me.setState({loading: false});
        });
    }
    render() {
        if (this.props.assets.length === 0) {
            return <NoAssetsFound />;
        }

        const columns = [
            {
                name: 'Title',
                selector: 'title',
                sortable: true
            },
            {
                name: 'Selections',
                selector: 'annotation_count',
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
                format: formatDay,
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
                    fontSize: '16px',
                    minHeight: '33px'
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
                className="react-data-table"
                columns={columns}
                highlightOnHover
                striped
                sortServer
                progressPending={this.state.loading}
                progressComponent={<LoadingAssets />}
                onSort={this.handleSort}
                data={this.props.assets} />
        );
    }
}

CollectionListView.propTypes = {
    assets: PropTypes.array,
    onUpdateAssets: PropTypes.func.isRequired,
};
