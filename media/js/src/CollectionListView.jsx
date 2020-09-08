import React from 'react';
import PropTypes from 'prop-types';
import DataTable, { createTheme } from 'react-data-table-component';
import LoadingAssets from './alerts/LoadingAssets';
import NoAssetsFound from './alerts/NoAssetsFound';
import {
    formatDay, getAssets, getAssetType, getAssetUrl, getTerms
} from './utils';

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
            sortField = 'added';
        }

        const orderBy = sortDirection === 'asc' ? sortField : '-' + sortField;

        const me = this;
        getAssets(
            this.props.title, this.props.owner, this.props.tags,
            this.props.terms, this.props.date,
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

        const me = this;

        const columns = [
            {
                name: 'Title',
                selector: 'title',
                sortable: true,
                wrap: true,
                format: function(row) {
                    return (
                        <a
                            href={getAssetUrl(row.id)}
                            onClick={
                                (e) => me.props.enterAssetDetailView(e, row)
                            }>
                            {row.title}
                        </a>
                    );
                }
            },
            {
                name: 'Selections',
                selector: 'annotation_count',
                sortable: false
            },
            {
                name: 'Tags',
                selector: 'tags',
                sortable: false,
                wrap: true,
                format: function(row) {
                    if (row && row.tags) {
                        return row.tags.join(', ');
                    }

                    return row.tags;
                }
            },
            {
                name: 'Terms',
                selector: 'terms',
                sortable: false,
                wrap: true,
                format: function(row) {
                    if (row && row.annotations) {
                        return getTerms(row.annotations).join(', ');
                    }

                    return '';
                }
            },
            {
                name: 'Media',
                selector: 'primary_type',
                sortable: false,
                format: function(row) {
                    return getAssetType(row.primary_type);
                }
            },
            {
                name: 'Owner',
                selector: 'author.public_name',
                sortable: true,
                wrap: true
            },
            {
                name: 'Date',
                format: formatDay,
                selector: 'added',
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
                dense
                highlightOnHover
                striped
                progressPending={this.state.loading}
                progressComponent={<LoadingAssets />}
                sortServer
                defaultSortField="title"
                onSort={this.handleSort}
                data={this.props.assets} />
        );
    }
}

CollectionListView.propTypes = {
    assets: PropTypes.array,
    enterAssetDetailView: PropTypes.func.isRequired,
    onUpdateAssets: PropTypes.func.isRequired,

    // Filters
    owner: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.array,
    terms: PropTypes.array,
    date: PropTypes.string
};
