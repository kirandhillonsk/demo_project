'''
/**
 *@copyright : ToXSL Technologies Pvt. Ltd. < www.toxsl.com >
 *@author     : Shiv Charan  spaceeta < shiv@toxsl.com >
 *
 * All Rights Reserved.
 * Proprietary and confidential :  All information contained herein is, and remains
 * the property of ToXSL Technologies Pvt. Ltd. and its partners.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 *
 *
 */
 '''
from .views import *
from accounts import views
from django.contrib import admin
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import reverse_lazy, path


admin.autodiscover()

app_name = 'superuser'


urlpatterns = [
    url(r'^users-list$', UsersList, name='users_list'),
    url(r'^rvt-users$', RvtuserList, name='rvt_users'),
    url(r'^users-delete$', UserDelete, name='users_delete'),
    url(r'^users-search$', UserSearch, name='users_search'),
    url(r'^services$', AdminServices, name='admin_services'),
    url(r'^add-service-category$', AddServicecategory, name='add_service_category'),
    url(r'^search-service-category$', SearchServicecategory, name='search_service_category'),
    url(r'^search-sub-admin$', SearchSubAdmin, name='search_sub_admin'),
    url(r'^SearchPetType$', SearchPetType, name='SearchPetType'),
    url(r'^search-rvt-user$', RvtSearch, name='search_rvt_user'),
    url(r'^delete-service-category$', DeleteServicecategory, name='delete_service_category'),
    url(r'^pervious-category-data$', PreviousCategoryData, name='pervious_category_data'),
    url(r'^service-category-edit$', ServiceCategoryEdit, name='service_category_edit'),
    url(r'^accept-reject-application$', AccpetRjectApplication, name='accept_reject_application'),
    url(r'^appointments$', AppointmentManagement, name='appointment_management'),
    url(r'^announcement-list$', AnnouncementsList, name='announcement_list'),
    url(r'^add-announcement$', AddAnnouncementView, name='add_announcement'),
    url(r'^delete-announcement$', DeleteAnnouncement, name='delete_announcement'),
    url(r'^change-target$', ChangeTarget, name='change_target'),
    url(r'^change-status$', ChangeStatus, name='change_status'),
    url(r'^filter-announcement$', FilterAnnouncement, name='filter_announcement'),
    url(r'^search-announcement$', SearchAnnouncement, name='search_announcement'),
    url(r'^search-appointments$', Search_Appointments, name='search_appointments'),


    
    url(r'^admin-profile$', AdminProfile, name='admin_profile'),
    url(r'^admin-profile-image$', AdminProfileImage, name='admin_profile_image'),
    url(r'^edit-user-info$', AdminEditUserProfile, name='edit_user_info'),
    url(r'^email-validation$', Email_Validation, name='email_validation'),
    url(r'^subscribed-user$', SubscribedUser, name='subscribed_user'),
    url(r'^contact-details$', ContactUSView, name='contact_details'),
    url(r'^admin-pet-type$', AdminPetType, name='admin_pet_type'),
    url(r'^add-pet-type$', AddPetType, name='add_pet_type'),
    url(r'^delete_pet_type$', DeletePettype, name='delete_pet_type'),
    url(r'^pet-type-edit$', PettypeEdit, name='pet_type_edit'),
    url(r'^previous-pet-type-data$', PreviousPettypeData, name='previous_pet_type_data'),
    url(r'^reject-application/(?P<id>[-\w]+)/$', RejectApplication, name='reject_application'),
    url(r'^search-rvt/', SearchRVT, name='search_rvt'),
    # url(r'^rvt-search/', RvtSearch, name='rvt_search'),

    url(r'^date-filter/', DateFilter, name='date_filter'),
    url(r'^sort-filter/', Sortfilter, name='sort_filter'),
    url(r'^User-AppointmentDetails/', User_AppointmentDetails, name='User_AppointmentDetails'),
    url(r'^mail_revert/', mail_revert, name='mail_revert'),
    url(r'^Print_appointment/', Print_appointment, name='Print_appointment'),
    path('delete_appointment_admin_index/',delete_appointment_admin_index,name='delete_appointment_admin_index'),
    path('search-index-admin/',Search_index_admin,name='search_index_admin'),
    path('recommendation/',recommendation,name='recommendation'),
    path('create_recommendation/',Create_recommendation,name='create_recommendation'),
    path('edit-recommendation/',Edit_recommendation,name='edit_recommendation'),
    path("Search-recommendation/",Search_recommendation,name='search_recommendation'),
    path('help-type/',Help_type,name='help_type'),
    path("assign-badge/",AssignBadge,name='assign_badge'),
    path('badge/',Badges,name='badge'),
    path('add-badge/',Add_badge,name='add_badge'),
    path('delete-badge',Delete_Badge,name='delete_badge'),
    path('edit-Badge/',Edit_Badge,name='edit_Badge'),
    path('search-badge/',Search_badge,name='search_badge'),
    path('previousBadgeData/',PreviousBadgeData,name='previousBadgeData'),
    path('add-banner/',AddBanner,name='add_banner'),
    path('delete-banner/',DeleteBanner,name='delete_banner'),
    path('previous-banner-data/',PreviousBannerData,name='previous_banner_data'),
    path('edit_banner/',EditBanner,name='edit_banner'),
    path('custom-requests/',CustomRequest,name='custom_requests'),
    path('sub-admin/',SubAdmin,name='sub_admin'),
    path('add-sub-admin/',AddSubAdmin,name='add_sub_admin'),
    path('delete-sub-admin/',DeleteSubAdmin,name='delete_sub_admin'),
    path('pervious-sub-admin-data/',PreviousSubAdminData,name='pervious_sub_admin_data'),
    path('sub-admin-edit/',SubAdminEdit,name='sub_admin_edit'),
    path('tax-management/',TaxManagement,name='tax_management'),
    path('add-tax-percentage/',AddTaxPercentage,name='add_tax_percentage'),
    path('previous-tax-percent/',PreviousTaxPercent,name='previous_tax_percent'),
    path('edit-tax-percentage/',EditTaxPercentage,name='edit_tax_percentage'),
    path('payouts-management/',PayoutsManagement,name='payouts_management'),

    path('release-payment/',PaymentRelease,name='payment_release'),
    path('search-help-admin/',Search_help_admin,name='search_help_admin'),
    path('multiple-search-custom/',Multiple_search_custom,name='multiple_search_custom'),
    path('sort-help-request/',Sort_help_request,name='sort_help_request'),
    path('payment-graph/',PaymentGraph,name='payment_graph'),
    path('job-opening/',CareerJobOpening,name='job_opening'),
    path('add-job-openings/',AddJobOpenings,name='add_job_openings'),
    path('delete-job-opening/',DeleteJobOpening,name='delete_job_opening'),
    path('previous-job-data/',PreviousJobData,name='previous_job_data'),
    path('job-title-edit/',JobTitleEdit,name='job_title_edit'),
    path('job-applicant-list/',JobApplicantList,name='job_applicant_list'),
    path('delete-applicant/',DeleteApplicant,name='delete_applicant'),
    path('applicant-search/',ApplicantsSearch,name='applicant_search'),
    path('job-opening-search/',JobOpeningSearch,name='job_opening_search'),
    path('get-user-state/',GetUserState,name='get_user_state'),
    path('view-help-type/',View_help_type,name="view_help_type"),
    path('edit-help-type/',Edit_help_type,name='edit_help_type'),
    path('delete_help_type/',Delete_help_type,name='delete_help_type'),
    path('previous-helpype-data/',PreviousHelpypeData,name='previous_helpype_data'),
    path('search_help_type/',Search_help_type,name='search_help_type'),
    path('appointment-pdf/',AppointmentPDF,name='appointment_pdf'),
    path('reset-customer-ids/',ResetCustomerIds,name='reset_customerids'),
    path('edit-announcement/',EditAnnouncement,name='edit_announcement'),
    path('view-announcement/',ViewAnnouncement,name='view_announcement'),


    path('mileage-management/',MileageManagement,name='mileage_management'),
    path('add-mileage-percentage/',AddMileagePercentage,name='add_mileage_percentage'),
    path('edit-mileage-percentage/',EditMileagePercentage,name='edit_mileage_percentage'),
    path('previous-mileage-percent/',PreviousMileagePercent,name='previous_mileage_percent'),

    url(r'^impersonate/', include('impersonate.urls')),


]