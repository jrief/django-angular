# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.test import TestCase
from django.views.generic import View
from djangular.core.urlresolvers import get_url_patterns


# This is now deprecated way of reversing django urls in angular code, but both old tests and code should be
# kept to maintain backwards compatibility for now


class DummyView(View):
    pass

include2 = patterns('',
    url(r'^edit/$', DummyView.as_view(), name='edit'),
    url(r'^view/$', DummyView.as_view(), name='view'),
)

include1 = patterns('',
    url(r'^login/$', DummyView.as_view(), name='login'),
    url(r'^profile/', include(include2, namespace='profile')),
)

urlpatterns = patterns('',
    url(r'^$', DummyView.as_view(), name='home'),
    url(r'^learnmore/$', DummyView.as_view(), name='learnmore'),
    url(r'accounts/', include(include1, namespace='accounts')),
)


class UrlReverserTest(TestCase):
    pattern_dict = None

    def setUp(self):
        self.pattern_dict = get_url_patterns(urlpatterns)

    def test_all_urls_are_found(self):
        names = (
            'home',
            'learnmore',
            'accounts:login',
            'accounts:profile:edit',
            'accounts:profile:view'
        )
        for name in names:
            self.assertIn(name, self.pattern_dict)

    def test_root_urls_are_found(self):
        root_pattern_dict = get_url_patterns(urlpatterns, filter_namespaces=[None])
        names = (
            'home',
            'learnmore',
        )
        excluded = (
            'accounts:login',
            'accounts:profile:edit',
            'accounts:profile:view'
        )
        for name in names:
            self.assertIn(name, root_pattern_dict)
        for name in excluded:
            self.assertNotIn(name, root_pattern_dict)

    def test_accounts_urls_are_found(self):
        accounts_pattern_dict = get_url_patterns(urlpatterns, filter_namespaces=['accounts'])
        names = (
            'accounts:login',
        )
        excluded = (
            'home',
            'learnmore',
            'accounts:profile:edit',
            'accounts:profile:view'
        )
        for name in names:
            self.assertIn(name, accounts_pattern_dict)
        for name in excluded:
            self.assertNotIn(name, accounts_pattern_dict)

    def test_combined_urls_are_found(self):
        combined_pattern_dict = get_url_patterns(urlpatterns, filter_namespaces=['accounts:profile', None])
        names = (
            'home',
            'learnmore',
            'accounts:profile:edit',
            'accounts:profile:view'
        )
        excluded = (
            'accounts:login',
        )
        for name in names:
            self.assertIn(name, combined_pattern_dict)
        for name in excluded:
            self.assertNotIn(name, combined_pattern_dict)

    def test_simple_urls(self):
        self.assertEqual(self.pattern_dict['home'], '/')
        self.assertEqual(self.pattern_dict['learnmore'], '/learnmore/')

    def test_included_namespaces_in_pattern_names(self):
        self.assertIn('accounts:login', self.pattern_dict)

    def test_included_namespaces_regex_joining(self):
        self.assertEqual(self.pattern_dict['accounts:login'], '/accounts/login/')

    def test_included_namespaces_multiple_levels(self):
        self.assertIn('accounts:profile:edit', self.pattern_dict)
        self.assertEqual(self.pattern_dict['accounts:profile:edit'], '/accounts/profile/edit/')
