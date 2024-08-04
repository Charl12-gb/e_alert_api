# Process d'installation

1. python manage.py makemigrations

2. python manage.py migrate

3. python manage.py seed-permissions

4. python manage.py seed-superadmin

5. python manage.py seed-app


# Voici les descriptions pour chaque chemin (path) avec sa fonction respective :

**'' - views.home**** : **Affiche la page d'accueil du site.**

**'login' - LoginView.as_view()** : **Permet aux utilisateurs de se connecter au site.**

**'register' - User_view.register** : *Permet aux utilisateurs de s'inscrire sur le site.*

**'users' - User_view.users** : *Affiche la liste des utilisateurs enregistrés.*

**'update/int:user_id' - User_view.update** : *Permet de mettre à jour les informations d'un utilisateur spécifique.*

**'delete/int:user_id' - User_view.delete** : *Permet de supprimer un utilisateur spécifique.*

**'users/int:user_id' - User_view.user** : *Affiche les informations détaillées d'un utilisateur spécifique.*

**'logout' - LoginView.as_view()** : *Permet aux utilisateurs de se déconnecter du site.*

**'refresh-token' - TokenRefreshView.as_view()** : *Actualise le token d'authentification pour un utilisateur connecté.*

**'app-config/seed' - app_config.seedAppConfigurations** : *Initialise les configurations de l'application.*

**'permissions/seed' - app_config.seedPermissions** : *Initialise les permissions de l'application.*

**'roles/seed' - app_config.seedAdminRole** : *Initialise les rôles administrateurs de l'application.*

**'roles/add' - User_view.addRole** : *Ajoute un nouveau rôle.*

**'roles' - User_view.roles** : *Affiche la liste des rôles.*

**'roles/int:role_id' - User_view.role** : *Affiche les détails d'un rôle spécifique.*

**'roles/int:role_id/update' - User_view.updateRole** : *Met à jour un rôle spécifique.*

**'roles/int:role_id/delete' - User_view.deleteRole** : *Supprime un rôle spécifique.*

**'roles/int:role_id/attach_permissions' - User_view.attachPermissionsToRole** : *Attache des permissions à un rôle spécifique.*

**'roles/int:role_id/remove_permissions' - User_view.removePermissionsToRole** : *Supprime des permissions d'un rôle spécifique.*

**'users/int:user_id/roles/int:role_id/attach' - User_view.attachRole** : *Attache un rôle à un utilisateur spécifique.*

**'users/int:user_id/roles/int:role_id/remove' - User_view.removeRole** : *Supprime un rôle d'un utilisateur spécifique.*

**'users/int:user_id/add_permission/int:permission_id' - User_view.addSpecificPermissionToUser** : *Ajoute une permission spécifique à un utilisateur.*

**'exercices/add' - Exercice_view.addExercice** : *Ajoute un nouvel exercice.*

**'exercices/update/int:exercice_id' - Exercice_view.updateExercice** : *Met à jour un exercice spécifique.*

**'exercices/manager/int:manager_id' - Exercice_view.managerExercises** : *Affiche les exercices d'un manager spécifique.*

**'exercices/partner/int:partner_id' - Exercice_view.partnerExercises** : *Affiche les exercices d'un partenaire spécifique.*

**'exercices/exercice/int:exercice_id' - Exercice_view.exercice** : *Affiche les détails d'un exercice spécifique.*

**'exercices/' - Exercice_view.exercices** : *Affiche la liste de tous les exercices.*

**'exercices/delete/int:exercice_id' - Exercice_view.deleteExercice** : *Supprime un exercice spécifique.*

**'exercices/open-close/int:exercice_id' - Exercice_view.openOrCloseExercice** : *Ouvre ou ferme un exercice spécifique.*

**'exercices/assigne-manager/int:exercice_id/int:manager_id' - Exercice_view.assigneExerciceToManager** : *Assigne un exercice à un manager spécifique.*

**'exercices/assigne-partner/int:exercice_id/int:partner_id' - Exercice_view.assigneExerciceToPartner** : *Assigne un exercice à un partenaire spécifique.*

**'exercices/set-date/int:exercice_id' - Exercice_view.setExerciceDate** : *Définit les dates d'un exercice spécifique.*

**'partners/documents/str:manager_id/str:period/' - Exercice_view.listPartnerAndServiceWHereDocumentNotSent** : *Récupère les partenaires et les services liés aux documents non envoyés pour un gestionnaire spécifique et une période spécifiée.*

**'configurations/update/int:config_id/str:value' - Configuration_view.updateConfigurations** : *Met à jour les configurations de l'application.*

**'configurations/int:config_id' - Configuration_view.configuration** : *Affiche les détails d'une configuration spécifique.*

**'configurations/' - Configuration_view.configurations** : *Affiche la liste des configurations de l'application.*

**'documents/add' - Document_view.addDocument** : *Ajoute un nouveau document.*

**'documents/update/int:document_id' - Document_view.updateDocument** : *Met à jour un document spécifique.*

**'documents/int:document_id' - Document_view.document** : *Affiche les détails d'un document spécifique.*

**'documents/delete/int:document_id' - Document_view.deleteDocument** : *Supprime un document spécifique.*

**'documents/status/int:document_id' - Document_view.setDocumentStatus** : *Définit le statut d'un document spécifique.*

**'documents/active/int:document_id' - Document_view.activeOrUnactiveDocument** : *Active ou désactive un document spécifique.*

**'documents/update_file/int:document_id' - Document_view.updateDocumentFile** : *Met à jour le fichier d'un document spécifique.*

**'exercice_configurations/create' - Exercice_configuration_view.createExerciceConfiguration** : *Crée une nouvelle configuration d'exercice.*

**'exercice_configurations/retrieve/int:configuration_id' - Exercice_configuration_view.retrieveExerciceConfiguration** : *Affiche les détails d'une configuration d'exercice spécifique.*

**'exercice_configurations/update/int:configuration_id' - Exercice_configuration_view.updateExerciceConfiguration** : *Met à jour une configuration d'exercice spécifique.*

**'exercice_configurations/delete/int:configuration_id' - Exercice_configuration_view.deleteExerciceConfiguration** : *Supprime une configuration d'exercice spécifique.*

**'exercice_configurations/list' - Exercice_configuration_view.listExerciceConfigurations** : *Affiche la liste des configurations d'exercice.*

**'logs/create/int:user_id/str:action' - Log_view.createLog** : *Crée un nouveau journal d'activité.*

**'logs/retrieve/int:log_id' - Log_view.retrieveLog** : *Affiche les détails d'un journal d'activité spécifique.*

**'logs/update/int:log_id/str:action' - Log_view.updateLog** : *Met à jour un journal d'activité spécifique.*

**'logs/delete/int:log_id' - Log_view.deleteLog** : *Supprime un journal d'activité spécifique.*

**'logs/list' - Log_view.listLogs** : *Affiche la liste des journaux d'activité.*