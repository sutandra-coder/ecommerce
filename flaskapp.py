from flask import Flask
from flask import Blueprint


from ecommerce_login import ecommerce_login
from ecommerce_retailer import ecommerce_retailer
from ecommerce_customer import ecommerce_customer
from ecommerce_customer_new import ecommerce_customer_new
from ecommerce_customer_new_with_language import ecommerce_customer_new_with_language
from ecommerce_product import ecommerce_product
from ecommerce_discount import ecommerce_discount
from ecommerce_campaign import ecommerce_campaign
from ecommerce_organisation import ecommerce_organisation
from ecommerce_autoload import ecommerce_autoload
from react_customer import react_customer
from ecommerce_product_admin import ecommerce_product_admin
from retailer_customer_notification import retailer_customer_notification
from retailer_dashboard import retailer_dashboard
from retailer_customerdtls import ret_customerdtls
from ecommerce_order_history import ecommerce_order_history
from ecommerce_autopopulation import ecommerce_autopopulation
from ecommerce_employee import ecommerce_employee
from ecommerce_retail_store import ecommerce_retail_store
from retailer_notification_section import retailer_notification_section
from ecommerce_organisation_otp import ecommerce_organisation_otp
from ecommerce_product_log import ecommerce_product_log
from ecommerce_customer_admin import ecommerce_customer_admin
from ecommerce_customer_xcl_upload import ecommerce_customer_xcl_upload
from ecommerce_app_settings import ecommerce_app_settings
from ecommerce_product_export import ecommerce_product_export
from ecommerce_product_sync import ecommerce_product_sync
from ecommerce_customer_analysis import ecommerce_customer_analysis
from ecommerce_retailer_loyality import ecommerce_retailer_loyality
from ecommerce_customer_loyality import ecommerce_customer_loyality
from ecommerce_supplier import ecommerce_supplier
from retailer_filteringcustomer import filteringcustomer
from ecommerce_consumer_configuration import ecommerce_consumer_configuration
from amazon_textract import amazon_textract
from zoho_crm import zoho_crm
from zoho_crm_ecommerce_product import zoho_crm_ecommerce_product
from zoho_crm_pos import zoho_crm_pos
from social_photo import social_photo
from face_detection import face_detection
from ecommerce_emi import ecommerce_emi
from social_photo_face_recognition import social_photo_face_recognition
from social_photo_face_recognition_new import social_photo_face_recognition_new
from woocommerce_product import woocommerce_product
from ecommerce_promoter import ecommerce_promoter
from bakes_and_cakes import bakes_and_cakes
from ecommerce_transaction import ecommerce_transaction
from bakes_and_cakes_admin import bakes_and_cakes_admin
from test_database import test_database
from meprotect_mail import meprotect_mail
from studybreak_examsection import exam_section
from signup_section import signup_section
from face_recognition_with_amazon import face_recognition_with_amazon
from social_photo_face_recognition_with_amazon import social_photo_face_recognition_with_amazon
from student_examsection import student_exam_section
from dms_section import dms_section
from esi_payment import esi_payment
from AMMobile_product import AMMobile_product
from AMMobile_product_realme import AMMobile_product_realme
from AMMobile_product_vivo import AMMobile_product_vivo
from AMMobile_customer_import import AMMobile_customer_import
from AMMobile_customer_loyality_import import AMMobile_customer_loyality_import
from AMMobile_product_samsung import AMMobile_product_samsung
from AMMobile_product_oppo import AMMobile_product_oppo
from AMMobile_product_xiaomi import AMMobile_product_xiaomi
from AMMobile_product_oneplus import AMMobile_product_oneplus
from AMMobile_product_nokia import AMMobile_product_nokia
from AMMobile_product_motorola import AMMobile_product_motorola
from AMMobile_product_others import AMMobile_product_others
from ecommerce_customer_filteration import ecommerce_customer_filteration

from aws_resources import aws_resources
from aws_resources_upload import aws_resources_upload
app = Flask(__name__)


app.register_blueprint(ecommerce_login, url_prefix='/ecommerce_login')
app.register_blueprint(ecommerce_retailer, url_prefix='/ecommerce_retailer')
app.register_blueprint(ecommerce_customer, url_prefix='/ecommerce_customer')
app.register_blueprint(ecommerce_customer_new, url_prefix='/ecommerce_customer_new')
app.register_blueprint(ecommerce_customer_new_with_language, url_prefix='/ecommerce_customer_new_with_language')
app.register_blueprint(ecommerce_product, url_prefix='/ecommerce_product')
app.register_blueprint(ecommerce_discount, url_prefix='/ecommerce_discount')
app.register_blueprint(react_customer, url_prefix='/react_customer')
app.register_blueprint(ecommerce_organisation, url_prefix='/ecommerce_organisation')
app.register_blueprint(ecommerce_autoload, url_prefix='/ecommerce_autoload')
app.register_blueprint(ecommerce_product_admin, url_prefix='/ecommerce_product_admin')
app.register_blueprint(retailer_customer_notification, url_prefix='/retcustomer_notify')
app.register_blueprint(retailer_dashboard, url_prefix='/retailer_dashboard')
app.register_blueprint(ret_customerdtls, url_prefix='/ret_customerdtls')
app.register_blueprint(ecommerce_order_history, url_prefix='/order_historydtls')
app.register_blueprint(ecommerce_autopopulation, url_prefix='/ecommerce_autopopulation')
app.register_blueprint(ecommerce_employee, url_prefix='/ecommerce_employee')
app.register_blueprint(ecommerce_retail_store, url_prefix='/ecommerce_retail_store')
app.register_blueprint(retailer_notification_section, url_prefix='/ret_notification')
app.register_blueprint(ecommerce_organisation_otp, url_prefix='/ecommerce_organisation_otp')
app.register_blueprint(ecommerce_product_log, url_prefix='/ecommerce_product_log')
app.register_blueprint(ecommerce_customer_admin, url_prefix='/ecommerce_customer_admin')
app.register_blueprint(ecommerce_customer_xcl_upload, url_prefix='/ecommerce_customer_xcl_upload')
app.register_blueprint(ecommerce_app_settings, url_prefix='/ecommerce_app_settings')
app.register_blueprint(ecommerce_product_export, url_prefix='/ecommerce_product_export')
app.register_blueprint(ecommerce_product_sync, url_prefix='/ecommerce_product_sync')
app.register_blueprint(aws_resources,url_prefix='/aws_portal')
app.register_blueprint(aws_resources_upload,url_prefix='/aws_portal_upload')
app.register_blueprint(ecommerce_customer_analysis, url_prefix='/ecommerce_customer_analysis')
app.register_blueprint(ecommerce_retailer_loyality, url_prefix='/ecommerce_retailer_loyality')
app.register_blueprint(ecommerce_customer_loyality, url_prefix='/ecommerce_customer_loyality')
app.register_blueprint(ecommerce_supplier, url_prefix='/ecommerce_supplier')
app.register_blueprint(filteringcustomer, url_prefix='/filtercustomer_notify')
app.register_blueprint(ecommerce_consumer_configuration, url_prefix='/ecommerce_consumer_configuration')
app.register_blueprint(amazon_textract, url_prefix='/amazon_textract')
app.register_blueprint(zoho_crm, url_prefix='/zoho_crm')
app.register_blueprint(zoho_crm_ecommerce_product, url_prefix='/zoho_crm_ecommerce_product')
app.register_blueprint(zoho_crm_pos, url_prefix='/zoho_crm_pos')
app.register_blueprint(social_photo, url_prefix='/social_photo')
app.register_blueprint(face_detection, url_prefix='/face_detection')
app.register_blueprint(ecommerce_emi, url_prefix='/ecommerce_emi')
app.register_blueprint(social_photo_face_recognition, url_prefix='/social_photo_face_recognition')
app.register_blueprint(social_photo_face_recognition_new, url_prefix='/social_photo_face_recognition_new')
app.register_blueprint(woocommerce_product, url_prefix='/woocommerce_product')
app.register_blueprint(ecommerce_promoter, url_prefix='/ecommerce_promoter')
app.register_blueprint(bakes_and_cakes, url_prefix='/bakes_and_cakes')
app.register_blueprint(ecommerce_transaction, url_prefix='/ecommerce_transaction')
app.register_blueprint(bakes_and_cakes_admin, url_prefix='/bakes_and_cakes_admin')
app.register_blueprint(test_database, url_prefix='/test_database')
app.register_blueprint(meprotect_mail, url_prefix='/meprotect_mail')
app.register_blueprint(exam_section, url_prefix='/exam_section')
app.register_blueprint(signup_section, url_prefix='/signup_section')
app.register_blueprint(face_recognition_with_amazon, url_prefix='/face_recognition_with_amazon')
app.register_blueprint(social_photo_face_recognition_with_amazon, url_prefix='/social_photo_face_recognition_with_amazon')
app.register_blueprint(student_exam_section, url_prefix='/studentexam_section')
app.register_blueprint(dms_section, url_prefix='/dms_section')
app.register_blueprint(esi_payment, url_prefix='/esi_payment')
app.register_blueprint(AMMobile_product, url_prefix='/AMMobile_product')
app.register_blueprint(AMMobile_product_realme, url_prefix='/AMMobile_product_realme')
app.register_blueprint(AMMobile_product_vivo, url_prefix='/AMMobile_product_vivo')
app.register_blueprint(AMMobile_customer_import, url_prefix='/AMMobile_customer_import')
app.register_blueprint(AMMobile_customer_loyality_import, url_prefix='/AMMobile_customer_loyality_import')
app.register_blueprint(AMMobile_product_samsung, url_prefix='/AMMobile_product_samsung')
app.register_blueprint(AMMobile_product_oppo, url_prefix='/AMMobile_product_oppo')
app.register_blueprint(AMMobile_product_xiaomi, url_prefix='/AMMobile_product_xiaomi')
app.register_blueprint(AMMobile_product_oneplus, url_prefix='/AMMobile_product_oneplus')
app.register_blueprint(AMMobile_product_nokia, url_prefix='/AMMobile_product_nokia')
app.register_blueprint(AMMobile_product_motorola, url_prefix='/AMMobile_product_motorola')
app.register_blueprint(AMMobile_product_others, url_prefix='/AMMobile_product_others')
app.register_blueprint(ecommerce_customer_filteration, url_prefix='/ecommerce_customer_filteration')

if __name__ == '__main__':
	# app.register_blueprint(youngRB_blueprint)
	# app.register_blueprint(coupon)
	app.run(host='0.0.0.0',debug=True)