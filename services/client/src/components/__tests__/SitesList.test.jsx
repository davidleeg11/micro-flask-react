import React from 'react';
import { shallow } from 'enzyme';

import SitesList from '../SitesList';
import renderer from 'react-test-renderer';

const sites = [
  {
    'active': true,
    'id': 1,
    'site': 'michael'
  },
  {
    'active': true,
    'id': 2,
    'site': 'michaelherman'
  }
];

test('SitesList renders properly', () => {
  const wrapper = shallow(<SitesList sites={sites}/>);
  const element = wrapper.find('h4');
  expect(element.length).toBe(2);
  expect(element.get(0).props.children).toBe('michael');
});

test('SitesList renders a snapshot properly', () => {
  const tree = renderer.create(<SitesList sites={sites}/>).toJSON();
  expect(tree).toMatchSnapshot();
});
