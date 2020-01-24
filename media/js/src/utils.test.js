/* eslint-env jest */
import fs from 'fs';

import {
    filterObj
} from './utils';

it('filters an object appropriately', () => {
    const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
    const fakeAsset = JSON.parse(assetData);

    let filters = {
        title: null,
        owner: 'all'
    };
    expect(filterObj(fakeAsset, filters)).toBe(fakeAsset);

    filters = {
        title: null,
        owner: 'njn2118'
    };
    expect(filterObj(fakeAsset, filters)).toBe(fakeAsset);

    filters = {
        title: null,
        owner: 'abc123'
    };
    expect(filterObj(fakeAsset, filters)).toBe(null);

    filters = {
        title: null,
        owner: 'all',
        date: 'yesterday'
    };
    expect(filterObj(fakeAsset, filters)).toBe(null);

    filters = {
        title: null,
        owner: 'all',
        date: 'today'
    };
    expect(filterObj(fakeAsset, filters)).toBe(null);
});
