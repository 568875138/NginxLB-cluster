from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from nlb_proxy.tools import validateIP, unique_list_elements, validatePort
from nlb_proxy.models import TcpProxy
from .common import APISaltPushMixin

import re,json,os

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TCPProxyView(View, APISaltPushMixin):
    model = TcpProxy
    fields_required = ['proxy_domain_name','app_name','app_port','proxy_port','app_servers']
    fields_optional = ['app_servers_backup','description']
    pillar_attrs    = ['app_name','app_port','proxy_port','app_servers', 'app_servers_backup']

    def dataVerify(self):
        form_data = {k:v.strip() for k,v in self.post_data.items() if k in self.fields_required + self.fields_optional}

        ### Check fields required.
        for field in self.fields_required:
            if field not in form_data:
                return "ERROR: Field '%s' is required!" % field

        ### Check 'proxy_domain_name'
        if re.search('[^a-z0-9\-\.]', form_data['proxy_domain_name']):
            return "ERROR: Illegal value detected for field 'proxy_domain_name': '%s'" % form_data['proxy_domain_name']

        ### Check 'app_name'
        if re.search('[^a-zA-Z0-9\-\_]', form_data['app_name']):
            return "ERROR: Illegal value detected for field 'app_name': '%s'" % form_data['app_name']

        ### Check 'app_port' and 'proxy_port'
        for field in ['app_port', 'proxy_port']:
            if validatePort(form_data[field]):
                form_data[field] = int(form_data[field])
            else:
                return "ERROR: Illegal port number: '%s'" % form_data[field]

        ### Check 'app_servers'
        app_server_list = unique_list_elements(form_data['app_servers'].split('/'))
        for ip in app_server_list:
            if not validateIP(ip):
                return "ERROR Invalid IP found: '%s'" % ip
        form_data['app_servers'] = '/'.join(app_server_list)

        ### Check 'app_servers_backup'
        if form_data.get('app_servers_backup'):
            app_backup_server_list = unique_list_elements(form_data['app_servers_backup'].split('/'))
            for ip in app_backup_server_list:
                if not validateIP(ip):
                    return "ERROR Invalid IP found: '%s'" % ip
            form_data['app_servers_backup'] = '/'.join(app_backup_server_list)

        return form_data

    def checkExists(self, verified_data):
        filter_list =[{'proxy_domain_name':verified_data['proxy_domain_name']},
                      {'app_name':verified_data['app_name']},
                      {'proxy_port':verified_data['proxy_port']},
                     ]
        return self.checkExistsWithFilterList(filter_list)

    def normalSearch(self, search_value):
        return self.model.objects.filter(is_deleted = 0).filter(Q(proxy_domain_name__icontains= search_value )|Q(app_name__icontains= search_value )|Q(app_port__icontains= search_value )|Q(app_servers__icontains= search_value )|Q(app_servers_backup__icontains= search_value )|Q(proxy_port__icontains= search_value )|Q(description__icontains= search_value )|Q(add_user__username__icontains= search_value ))

    def searchData(self):
        legal_field_s = {'APP':'app_name',
                       'APP_PORT':'app_port',
                       'LISTEN_PORT':'proxy_port',
                       'USER':'add_user',
                       'DESC':'description',
                       'DOMAIN':'proxy_domain_name',
                      }
        legal_field_m = {'SERVER':['app_servers','app_servers_backup'],}
        search_value = self.request.GET.get('search_value')
        search_value_ns = search_value.replace(' ','')

        queryset = None
        if re.search('^([A-Z]+|[A-Z]+_[A-Z]+):[^&]+(&([A-Z]+|[A-Z]+_[A-Z]+):[^&]+)*$', search_value_ns):
            search_dict = { item.split(':')[0]:item.split(':')[1] for item in search_value_ns.split('&')}
            filter_dict = {'is_deleted':0}
            for k in search_dict:
                if k in legal_field_s:
                    filter_dict[ legal_field_s[k] + '__icontains'] = search_dict[k]

            queryset = self.model.objects.filter(**filter_dict)

            if 'SERVER' in search_dict:
                queryset = queryset.filter(Q(app_servers__icontains=search_dict['SERVER'])|Q(app_servers_backup__icontains=search_dict['SERVER']))

        elif re.search('^([A-Z]+|[A-Z]+_[A-Z]+)=[^&]+(&([A-Z]+|[A-Z]+_[A-Z]+)=[^&]+)*$', search_value_ns):
            search_dict = { item.split('=')[0]:item.split('=')[1] for item in search_value_ns.split('&')}
            filter_dict = {'is_deleted':0}
            for k in search_dict:
                if k in legal_field_s:
                    filter_dict[ legal_field_s[k]] = search_dict[k]
            queryset = self.model.objects.filter(**filter_dict)

            if 'SERVER' in search_dict:
                queryset = queryset.filter(Q(app_servers=search_dict['SERVER'])|Q(app_servers_backup=search_dict['SERVER']))

        if queryset is None:
            queryset = self.normalSearch(search_value)

        return queryset.order_by('-id')

    def makeDataList(self, queryset):
        data = []
        for obj in queryset:
            attrs = {'id': obj.id,
                    'proxy_domain_name': obj.proxy_domain_name,
                    'app_name': obj.app_name,
                    'app_port': obj.app_port,
                    'app_servers': obj.app_servers,
                    'app_servers_backup': obj.app_servers_backup,
                    'proxy_port': obj.proxy_port,
                    'description': obj.description,
                    'add_time': obj.add_time.strftime('%F %T'),
                    'add_user': obj.add_user.username,
                    'status': ['服务正常', 'green'],
                    }

            if obj.apply_stat == 0:
                attrs['status'] = ["下发中", "orange"]
            elif obj.apply_stat == 2:
                attrs['status'] = ["下发失败","red"]
            elif obj.apply_stat == 3:
                attrs['status'] = ["下发成功，等待reload","blue"]
            elif obj.is_disabled:
                attrs['status'] = ['已停用', "gray"]

            data.append(attrs)
        return data
