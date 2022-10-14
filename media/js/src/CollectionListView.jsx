import React from 'react';
import PropTypes from 'prop-types';
import { styled } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses }  from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import NoAssetsFound from './alerts/NoAssetsFound';
import {
    formatDay, getAssetType, getAssetUrl, getTerms
} from './utils';

function createDate(name, selection, tags, vocabulary, media, owner, date) {
    return { name, selection, tags, vocabulary, media, owner, date };
}

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: '#cacbcc',
        color: theme.palette.common.black,
        fontSize: 16
    }
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
    '&:nth-of-type(odd)': {
        backgroundColor: theme.palette.action.hover,
    },
    // hide last border
    '&:last-child td, &:last-child th': {
        border: 1,
        margin: 1
    },
}));

export default class CollectionListView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false
        };
    }
    render() {
        if (this.props.assets.length === 0) {
            return <NoAssetsFound />;
        }

        const me = this;

        const rows = [];

        me.props.assets.map((asset, index) => {
            let name = <a
                href={getAssetUrl(asset.id)}
                key={index}
                onClick={(e) => me.props.enterAssetDetailView(e, asset)}>
                {asset.title}
            </a>;
            let selection = asset.annotation_count;
            let tags = asset.tags.join(', ');
            let media = getAssetType(asset.primary_type);
            let owner = asset.author.public_name;
            let date = formatDay(asset);
            let vocabulary = getTerms(asset.annotations).join(', ');
            rows.push(createDate(
                name, selection, tags, vocabulary, media, owner, date));
        });

        return (
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                        <TableRow>
                            <StyledTableCell>Title</StyledTableCell>
                            <StyledTableCell align="right">
                                Selections
                            </StyledTableCell>
                            <StyledTableCell align="right">
                                Tags
                            </StyledTableCell>
                            <StyledTableCell align="right">
                                Course Vocabulary
                            </StyledTableCell>
                            <StyledTableCell align="right">
                                Media
                            </StyledTableCell>
                            <StyledTableCell align="right">
                                Owner
                            </StyledTableCell>
                            <StyledTableCell align="right">
                                Date
                            </StyledTableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map((row) => (
                            <StyledTableRow
                                key={row.name}
                            >
                                <TableCell component="th" scope="row">
                                    {row.name}
                                </TableCell>
                                <TableCell align="right">
                                    {row.selection}
                                </TableCell>
                                <TableCell align="right">
                                    {row.tags}
                                </TableCell>
                                <TableCell align="right">
                                    {row.vocabulary}
                                </TableCell>
                                <TableCell align="right">
                                    {row.media}
                                </TableCell>
                                <TableCell align="right">
                                    {row.owner}
                                </TableCell>
                                <TableCell align="right">
                                    {row.date}
                                </TableCell>
                            </StyledTableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
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
