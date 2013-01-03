from django.conf.urls.defaults import patterns, url
from ietf.nomcom.forms import EditChairForm, EditChairFormPreview, \
                              EditMembersForm, EditMembersFormPreview

urlpatterns = patterns('ietf.nomcom.views',
    url(r'^(?P<year>\d{4})/private/$', 'private_index', name='nomcom_private_index'),
    url(r'^(?P<year>\d{4})/private/merge/$', 'private_merge', name='nomcom_private_merge'),
    url(r'^(?P<year>\d{4})/private/edit-members/$', EditMembersFormPreview(EditMembersForm), name='nomcom_edit_members'),
    url(r'^(?P<year>\d{4})/private/edit-chair/$', EditChairFormPreview(EditChairForm), name='nomcom_edit_chair'),
    url(r'^(?P<year>\d{4})/private/edit-publickey/$', 'edit_publickey', name='nomcom_edit_publickey'),

    url(r'^(?P<year>\d{4})/$', 'index', name='nomcom_index'),
    url(r'^(?P<year>\d{4})/requirements/$', 'requirements', name='nomcom_requirements'),
    url(r'^(?P<year>\d{4})/questionnaires/$', 'questionnaires', name='nomcom_questionnaires'),
    url(r'^(?P<year>\d{4})/comments/$', 'comments', name='nomcom_comments'),
    url(r'^(?P<year>\d{4})/nominate/$', 'nominate', name='nomcom_nominate'),
    url(r'^ajax/position-text/(?P<position_id>\d+)/$', 'ajax_position_text', name='nomcom_ajax_position_text'),

)
