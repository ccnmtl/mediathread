import isFinite from 'lodash/isFinite';
import Cookies from 'js-cookie';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method='get', data=null) {
    const token = Cookies.get('csrftoken');
    return fetch(url, {
        method: method,
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token
        },
        body: data,
        credentials: 'same-origin'
    });
};

const getAssets = function(
    title='', owner='', tags=[], terms=[], date='all',
    offset=0
) {
    const params = new URLSearchParams();

    // Pagination
    params.append('limit', 20);
    params.append('offset', offset);

    // Always include the annotations
    params.append('annotations', true);

    if (title) {
        params.append('search_text', title);
    }

    if (date !== 'all') {
        params.append('modified', date);
    }

    if (tags && tags.length > 0) {
        params.append('tag', tags.map(tag => tag.value));
    }

    if (terms && terms.length > 0) {
        terms.forEach(function(term) {
            params.append(`vocabulary-${term.data.vocab_id}`, term.data.id);
        });
    }

    let basePath = '/api/asset/';
    if (owner && owner !== 'all') {
        basePath = `/api/asset/user/${owner}/`;
    }

    return authedFetch(basePath + '?' + params.toString())
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading assets: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

/**
 * Get annotation metadata.
 */
const getAsset = function(id=null) {
    let url = '/asset/';
    if (id) {
        url = `/api/asset/${id}/?annotations=true`;
    }
    return authedFetch(url)
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const createSelection = function(assetId, data) {
    return authedFetch(
        `/asset/create/${assetId}/annotations/`,
        'post',
        JSON.stringify(data)
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error making selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const deleteSelection = function(assetId, selectionId) {
    return authedFetch(
        `/asset/delete/${assetId}/annotations/${selectionId}/`,
        'post'
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error deleting selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const getHours = function(totalSeconds) {
    return Math.floor(totalSeconds / 3600);
};

const getMinutes = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const seconds = totalSeconds - (hours * 3600);
    return Math.floor(seconds / 60);
};

const getSeconds = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
    const seconds = totalSeconds - (hours * 3600) - (minutes * 60);
    return Math.floor(seconds);
};

/**
 * Given a number of seconds as a float, return an array
 * containing [hours, minutes, seconds].
 */
const getSeparatedTimeUnits = function(totalSeconds) {
    return [
        getHours(totalSeconds),
        getMinutes(totalSeconds),
        getSeconds(totalSeconds)
    ];
};

const parseTimecode = function(str) {
    const parts = str.split(':');
    const col1 = Number(parts[0]);
    const col2 = Number(parts[1]);
    const col3 = Number(parts[2]);
    if (isFinite(col1) && isFinite(col2) && isFinite(col3)) {
        return (col1 * 60) + col2 + (col3 / 100);
    } else {
        return null;
    }
};

const pad2 = function(number) {
    return (number < 10 ? '0' : '') + number;
};

const formatTimecode = function(totalSeconds) {
    const units = getSeparatedTimeUnits(totalSeconds);
    return pad2(units[0]) + ':' + pad2(units[1]) + ':' + pad2(units[2]);
};

export {
    getAssets, getAsset, createSelection, deleteSelection,
    getHours, getMinutes, getSeconds,
    pad2, getSeparatedTimeUnits, formatTimecode, parseTimecode
};
