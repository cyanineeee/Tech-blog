from django.utils.safestring import mark_safe
import copy

'''
使用Pagination:
在view中
def order_manage(request):
    queryset = Orderform.objects.all() #先从数据库中获取所有的数据

    page_object = Pagination(request,queryset) #实例化
    page_queryset = page_object.page_queryset #获取符合要求的（指定页码中现实的）查询数据
    page_html_str = page_object.html() #获取组装好的页码下标html
    return render(request,'order.html',{
        'page_queryset' :page_queryset, #返回展示数据
        'page_html_str' : page_html_str #返回下方页码的html代码
    })

在前端html
    #数据内容
    {% if page_queryset %}
        {% for order in page_queryset %}
            <tr>
                <th >{{ order.id }}</th>
                <td>{{order.starttime | date:'Y-m-d H:i:s'}}</td>
                <td>{{order.presettime | date:'Y-m-d H:i:s'}}</td>
                <td>{{order.endtime | date:'Y-m-d H:i:s'}}</td>
                <td>{{order.customer}}</td>
                <td>{{order.amount}}</td>
                <td>{{order.commodity}}</td>
                <td>{{order.get_status_display}}</td>
                <td><a href="{% url 'order_edit' order.id %}"><button type="button " class="btn btn-warning btn-sm">修改信息</button></a></td>
                <td><a href="{% url 'order_delete' order.id %}"><button type="button" class="btn btn-sm btn-danger">删除</button></a></td>
            </tr>
        {% endfor %}
    {% endif %}

    #页码内容
    <ul class="pagination justify-content-end">
    {% if page_html_str %}
        {{page_html_str}}
    {% else %}
        <li class="page-item">
        <a class="page-link disabled">前一页</a>
        </li>
        <li class="page-item active"><a class="page-link" href="?page=1">1</a></li>
        <li class="page-item">
        <a class="page-link disabled">后一页</a>
        </li>
    {% endif %}
    </ul>


'''

class Pagination(object):
    def __init__(self,request,queryset,page_param='page',page_size=10,plus=5):
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param

        page = request.GET.get(self.page_param,'1')
        if page.isdecimal(): #如果是一个数字 合法输入
            page = int(page)
        else:  #非法输入 
            page = 1
        self.page = page #当前页码
        self.page_size = page_size #每页显示内容
        self.start = (page - 1) * page_size  #每页第一个数据序号
        self.end = page * page_size  #每页最后一个序号
        self.page_queryset =queryset[self.start:self.end]  #当前页面的数据集合
        total_count = queryset.count() #数据库总条
        total_pages , div = divmod(total_count,page_size)
        if div:
            total_pages += 1
        self.total_pages = total_pages
        self.plus = plus
        # print(self.page_queryset,total_count,self.total_pages)

    def html(self):
        #计算出前五页后五页
        if self.total_pages <= 2 * self.plus + 1: #数据库中的数据少于11页
            start_page = 1
            end_page = self.total_pages
        else:  
            #除非页数不够 不然始终展示11页 需要是一个奇数 前后 = plus * 2 再加上当前的页面
            #数据库中的数据多于11页
            if self.page <= self.plus: #当前页码的前面的页面数量 < 5 
                start_page = 1
                end_page = 2 * self.plus + 1 #展示从第一页到第
            else: #当前页 > 5 
                if (self.page + self.plus ) > self.total_pages: #当前页码+5 > 总页数
                    start_page = self.total_pages - 2 * self.plus
                    end_page = self.total_pages
                else:  #当前页码 + 5 < 总页数
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus + 1 

        page_str_list = []

        #首页
        self.query_dict.setlist(self.page_param,[1])
        page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">首页</a></li>')

        #上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param,[self.page - 1])
            page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">上一页</a></li>')
        else:  #就是首页
            self.query_dict.setlist(self.page_param,[1])
            page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">上一页</a></li>') #默认上一页还是第一页

        #页面
        for i in range(start_page,end_page + 1):
            self.query_dict.setlist(self.page_param,[i])
            if i == self.page: #当前页面需要添加active属性
                page_str_list.append(f'<li class="page-item active"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>')
            else:
                page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>')

        #下一页
        if self.page < self.total_pages: #当前不是最后一页
            self.query_dict.setlist(self.page_param,[self.page + 1])
            page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">下一页</a></li>')
        else: #当前是最后一页
            self.query_dict.setlist(self.page_param,[self.total_pages])
            page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">下一页</a></li>')
            
        #尾页
        self.query_dict.setlist(self.page_param,[self.total_pages])
        page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">尾页</a></li>')

        search_html_str = '''
                <li style="margin-left:5px;">
                <form class="d-flex" role="search" method="get">
                    <input class="form-control me-2" type="search" name="page" placeholder="页码" aria-label="Search">
                    <button class="btn btn-outline-success btn-sm" type="submit" style="width:150px">转跳</button>
                </form>                
              </li>'''
        page_str_list.append(search_html_str)

        page_string = mark_safe(''.join(page_str_list))
        return page_string

