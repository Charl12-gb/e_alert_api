from . import views
from django.urls import path
from .views import LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from .my_views.Exercice_views import Exercice_view
from .my_views.Document_views import Document_view
from .my_views.Exercice_configuration_views import Exercice_configuration_view
from .my_views.Log_views import Log_view
from .my_views.user_views import User_view
from .my_views.configuration_views import Configuration_view
from .my_views.Collaboration_views import Collaboration_view
from .my_views.Contact_views import Contact_view
from .my_views import Statistique

urlpatterns = [
    path('', views.home),
    path('login', LoginView.as_view(), name='login'),
    path('register', User_view.register, name='register'),
    path('users', User_view.users, name='users'),
    path('users/<str:user_type>', User_view.usersByType, name='users_by_type'),
    path('update/<int:user_id>', User_view.update, name='update'),
    path('delete/<int:user_id>', User_view.delete, name='delete'),
    path('user-detail/<int:user_id>', User_view.user, name='user'),
    path('update/user/<int:id>/password', User_view.updatePassword),
    path('reset-password', User_view.resetPassword, name="reset-password"),
    path('users-set-status/<int:user_id>', User_view.activeOrInactiveUser),
    path('users_partner_free-is_active', User_view.getUserPartnerActiveAndFree),
    path('get-current-user', User_view.getCurrentUser, name='current_user'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh-token', TokenRefreshView.as_view(), name='token_refresh'),

    # Roles & Permissions
    path('roles/add', User_view.addRole),
    path('roles', User_view.roles),
    path('roles/<int:role_id>', User_view.role),
    path('roles/<int:role_id>/update', User_view.updateRole),
    path('roles/<int:role_id>/delete', User_view.deleteRole),
    path('roles/<int:role_id>/attach_permissions', User_view.attachPermissionsToRole),
    path('roles/<int:role_id>/remove_permissions', User_view.removePermissionsToRole),
    path('users/<int:user_id>/roles/<int:role_id>/attach', User_view.attachRole),
    path('users/<int:user_id>/roles/<int:role_id>/remove', User_view.removeRole),
    path('users/<int:user_id>/add_permission/<int:permission_id>', User_view.addSpecificPermissionToUser),
    path('users/<int:user_id>/remove_permission/<int:permission_id>', User_view.removeSpecificPermissionToUser),
    path('users-permissions/<int:user_id>', User_view.getUserPermissions),
    path('roles-permissions/<int:role_id>', User_view.getRolePermissions),
    path('permissions', User_view.getPermissions),

    # Collaboration
    path('associate-partner-to-manager/', Collaboration_view.associatePartnerToManager, name='associate-partner-to-manager'),
    path('remove-manager-partner/<int:collaboration_id>/', Collaboration_view.removeManagerPartner, name='remove-manager-partner'),
    path('manager-partner-lists/<str:manager_id>/', Collaboration_view.managerPartnerLists, name='manager-partner-lists'),
    path('get-manager-partner-documents/<str:manager_id>/<str:partner_id>/', Collaboration_view.getManagerPartnerDocuments, name='get-manager-partner-documents'),
    path('get-partner-documents/<str:partner_id>/', Collaboration_view.getPartnerDocuments, name='get-partner-documents'),
    path('get-manager-partner-documents-by-service/<str:manager_id>/<str:partner_id>/<str:service_id>/', Collaboration_view.getManagerPartnerDocumentsByService, name='get-manager-partner-documents-by-service'),
    path('get-partner-documents-by-service/<str:partner_id>/<str:service_id>/', Collaboration_view.getPartnerDocumentsByService, name='get-partner-documents-by-service'),

    # Exercice
    path('exercices/', Exercice_view.exercices),
    path('exercices/add', Exercice_view.addExercice),
    path('exercices/update/<int:exercice_id>', Exercice_view.updateExercice),
    path('exercices/exercice/<int:exercice_id>', Exercice_view.exercice),
    path('exercices/delete/<int:exercice_id>', Exercice_view.deleteExercice),
    path('exercices/open-close/<int:exercice_id>', Exercice_view.openOrCloseExercice),
    path('exercices/set-date/<int:exercice_id>', Exercice_view.setExerciceDate),
    path('users-detail-data/<int:user_id>', Exercice_view.getDetailData),
    path('partners/documents/<str:manager_id>/<str:period>/', Exercice_view.listPartnerAndExerciceWhereDocumentNotSent),
    path('renew-exercise-for-year', Exercice_view.renewForYear),

    # Configurations
    path('configurations/update/<int:config_id>/<str:value>', Configuration_view.updateConfigurations),
    path('configurations/<int:config_id>', Configuration_view.configuration),
    path('configurations', Configuration_view.configurations),

    # Documents
    path('documents/add', Document_view.addDocument),
    path('documents/update/<int:document_id>', Document_view.updateDocument),
    path('documents/<int:document_id>', Document_view.document),
    path('documents/partner/<int:partner_id>', Document_view.getPartnerDocuments),
    path('documents/assigne-partner', Document_view.assignDocumentToPartner),
    path('documents/delete/<int:document_id>', Document_view.deleteDocument),
    path('documents/status/<int:document_id>', Document_view.setDocumentStatus),
    path('documents/active/<int:document_id>', Document_view.activeOrUnactiveDocument),
    path('documents/update_file/<int:document_id>', Document_view.updateDocumentFile),
    path('documents/manager-partner-documents/<int:manager_id>', Document_view.getListDocForManagerPartner),
    path('documents/download/<int:document_id>', Document_view.download_document, name='download_document'),

    # Exercice configurations
    path('document_configurations/create', Exercice_configuration_view.createOrUpdateDocumentConfiguration),
    path('document_configurations/retrieve/<int:document_id>', Exercice_configuration_view.retrieveConfigurationByDocuments),
    path('document_configurations/delete/<int:configuration_id>', Exercice_configuration_view.deleteDocumentConfiguration),
    path('document_configurations/list', Exercice_configuration_view.listDocumentConfigurations),

    # Logs
    path('logs/create/<int:user_id>/<str:action>', Log_view.createLog),
    path('logs/retrieve/<int:log_id>', Log_view.retrieveLog),
    path('logs/update/<int:log_id>/<str:action>', Log_view.updateLog),
    path('logs/delete/<int:log_id>', Log_view.deleteLog),
    path('logs/list', Log_view.listLogs),

    # Contacts
    path('add-contact', Contact_view.addContact),
    path('contact/<int:contact_id>', Contact_view.contact),
    path('contacts', Contact_view.contacts),
    path('contacts-active', Contact_view.activeContacts),
    path('set-contact/<int:contact_id>', Contact_view.activeOrInactiveContact),
    path('update-contact/<int:contact_id>', Contact_view.updateContact),
    path('add-update-contact', Contact_view.addOrUpdateContact),

    # Statistique
    path('exercise-status-distribution', Statistique.exerciseStatusDistribution),
    path('documents-per-periodicity', Statistique.documentsPerPeriodicity),
    path('collaborations-per-month', Statistique.collaborationsPerMonth),
    path('exercise-status-document', Statistique.documentStatusDistribution),
    path('get-statistics', Statistique.getStatistics),
    path('get-reports', Statistique.getReports),
]
