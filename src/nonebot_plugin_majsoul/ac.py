from nonebot_plugin_access_control_api.service import create_plugin_service

plugin_service = create_plugin_service("nonebot_plugin_majsoul")

query_info_service = plugin_service.create_subservice("query_info")
query_records_service = plugin_service.create_subservice("records")
pt_plot_service = plugin_service.create_subservice("pt_plot")
majsoul_binding = plugin_service.create_subservice("paifuya_binding")

paipu_service = plugin_service.create_subservice("paipu_download")
