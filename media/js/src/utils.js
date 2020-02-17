import Cookies from 'js-cookie';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method = 'get', data = null) {
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
const getAsset = function() {
    return authedFetch('/asset/')
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

export {getAssets, getAsset};
