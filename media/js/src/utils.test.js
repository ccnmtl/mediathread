/* eslint-env jest */

import {
    formatTimecode, pad2,
    getSeparatedTimeUnits, parseTimecode,
    groupByTag, getTagName
} from './utils';


describe('formatTimecode', () => {
    it('formats minutes correctly', () => {
        expect(formatTimecode(0)).toBe('00:00');
        expect(formatTimecode(55 * 60)).toBe('55:00');
        expect(formatTimecode(60 * 60)).toBe('01:00:00');
        expect(formatTimecode(81 * 60)).toBe('01:21:00');
        expect(formatTimecode(9999 * 60)).toBe('166:39:00');
    });
    it('formats seconds correctly', () => {
        expect(formatTimecode(0.2398572)).toBe('00:00');
        expect(formatTimecode(55.1871)).toBe('00:55');
        expect(formatTimecode(60.1241)).toBe('01:00');
        expect(formatTimecode(81.3299)).toBe('01:21');
        expect(formatTimecode(9999.114)).toBe('02:46:39');
        expect(formatTimecode(1.999602)).toBe('00:01');
    });
});

describe('parseTimecode', () => {
    it('parses timecodes correctly', () => {
        expect(parseTimecode('00:00')).toBe(0);
        expect(parseTimecode('00:00:00')).toBe(0);
        expect(parseTimecode('00:55:00')).toBe(3300);
        expect(parseTimecode('01:00:00')).toBe(3600);
        expect(parseTimecode('01:21:00')).toBe(4860);
        expect(parseTimecode('166:39:00')).toBe(599940);
        expect(parseTimecode('00:00:23')).toBe(23);
        expect(parseTimecode('00:55:18')).toBe(3318);
        expect(parseTimecode('55:18')).toBe(3318);
        expect(parseTimecode('01:00:12')).toBe(3612);
        expect(parseTimecode('01:21:32')).toBe(4892);
        expect(parseTimecode('166:39:11')).toBe(599951);
        expect(parseTimecode('00:01:99')).toBe(159);
        expect(parseTimecode('01:99')).toBe(159);
        expect(parseTimecode('01:00')).toBe(60);

        // Flexible about invalid chars, in some cases.
        expect(parseTimecode('x0:0:12')).toBe(12);
    });
    it('is flexible about zeroes', () => {
        expect(parseTimecode('00:00:0')).toBe(0);
        expect(parseTimecode('0:0:0')).toBe(0);
        expect(parseTimecode('00:0')).toBe(0);
        expect(parseTimecode('0:00:0')).toBe(0);
        expect(parseTimecode('0:00:00')).toBe(0);
        expect(parseTimecode('0:55:00')).toBe(3300);
        expect(parseTimecode('00:0:12')).toBe(12);
    });
    it('returns null on invalid input', () => {
        expect(parseTimecode('00:aa:0')).toBeNull();
        expect(parseTimecode('0:00gfw0')).toBeNull();
        expect(parseTimecode('0:00:f0')).toBeNull();
        expect(parseTimecode('0:55:w0')).toBeNull();
    });
});

describe('getSeparatedTimeUnits', () => {
    it('returns the correct values', () => {
        expect(getSeparatedTimeUnits(0)).toEqual([0, 0, 0]);
        expect(getSeparatedTimeUnits(0.01)).toEqual([0, 0, 0]);
        expect(getSeparatedTimeUnits(110.01)).toEqual([0, 1, 50]);
        expect(getSeparatedTimeUnits(110.99)).toEqual([0, 1, 50]);
    });
});

describe('pad2', () => {
    it('pads a low number with a zero', () => {
        expect(pad2(0)).toBe('00');
        expect(pad2(4)).toBe('04');
    });
    it('doesn\'t pad high numbers', () => {
        expect(pad2(10)).toBe('10');
        expect(pad2(99)).toBe('99');
        expect(pad2(100)).toBe('100');
    });
});

describe('groupByTag', () => {
    it('accepts an empty array', () => {
        expect(groupByTag([])).toStrictEqual([]);
    });
});

describe('getTagName', () => {
    it('accepts an empty array', () => {
        expect(getTagName(123, [])).toBe('No Tags');
        expect(getTagName(0, [])).toBe('No Tags');
    });
});
